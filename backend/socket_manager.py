from fastapi import WebSocket
from typing import List, Dict
import json
import redis.asyncio as redis
import os

class ConnectionManager:
    def __init__(self):
        # Store connection info: {client_id: {"ws": WebSocket, "lang": str}}
        self.active_connections: Dict[str, Dict] = {}
        self.redis = None
        self.pubsub = None
        # Try to connect to Redis, but don't fail if it's not available
        try:
            self.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            self.pubsub = self.redis.pubsub()
        except Exception as e:
            print(f"Redis not available: {e}")

    async def connect(self, websocket: WebSocket, client_id: str, preferred_lang: str = "eng_Latn"):
        await websocket.accept()
        self.active_connections[client_id] = {
            "ws": websocket,
            "lang": preferred_lang
        }
        # Subscribe to this client's channel in Redis to receive messages from other workers
        # We need a separate task for listening to Redis
        # For simplicity in this MVP, we will just have a global broadcast channel
        pass

    def disconnect(self, client_id: str, websocket: WebSocket):
        if client_id in self.active_connections:
            # Only remove if the websocket matches (prevents race condition during reconnect)
            if self.active_connections[client_id]["ws"] == websocket:
                del self.active_connections[client_id]

    async def broadcast(self, message_data: dict, exclude_client_id: str = None):
        """
        Broadcasts a message to all connected clients, translating it to their preferred language.
        message_data: {"content": str, "sender": str, "original_lang": str}
        """

        from main import get_translation_service_async, is_model_loaded # Avoid circular import
        
        # Check if model is loaded, if not, notify everyone (or just the relevant people)
        model_was_loading = False
        if not is_model_loaded():
            model_was_loading = True
            print("Model not loaded. Notifying clients...")
            loading_msg = {
                "type": "status",
                "status": "loading_model",
                "content": "Initializing translation model (this may take a few seconds)..."
            }
            # Broadcast loading status to all connected clients
            for connection_info in self.active_connections.values():
                try:
                    await connection_info["ws"].send_text(json.dumps(loading_msg))
                except:
                    pass

        ts = await get_translation_service_async()

        if model_was_loading:
            loaded_msg = {
                "type": "status",
                "status": "loaded",
                "content": "Model Loaded"
            }
            for connection_info in self.active_connections.values():
                try:
                    await connection_info["ws"].send_text(json.dumps(loaded_msg))
                except:
                    pass
        
        # 1. Send to local connections
        print(f"Broadcasting message to {len(self.active_connections)} clients. Exclude: {exclude_client_id}")
        for client_id, connection_info in self.active_connections.items():
            # Skip the sender to avoid echo (frontend handles optimistic updates)
            if client_id == exclude_client_id:
                print(f"Skipping sender {client_id}")
                continue
                
            try:
                target_lang = connection_info["lang"]
                source_text = message_data.get("content", "")
                source_lang = message_data.get("original_lang", "eng_Latn")
                sender_id = message_data.get("sender", "unknown")
                
                print(f"Processing for {client_id} (Lang: {target_lang})")
                
                # Don't translate if languages match
                if source_lang == target_lang:
                    translated_text = source_text
                    latency_ms = 0
                else:
                    # Notify client that translation is in progress
                    status_msg = {
                        "type": "status",
                        "status": "translating",
                        "content": "Translating message...",
                        "sender": sender_id
                    }
                    await connection_info["ws"].send_text(json.dumps(status_msg))

                    # Translate
                    import time
                    start_time = time.time()
                    translated_text = ts.translate(source_text, source_lang, target_lang)
                    latency_ms = (time.time() - start_time) * 1000
                
                response = {
                    "original": source_text,
                    "translated": translated_text,
                    "sender": sender_id,
                    "target_lang": target_lang,
                    "latency_ms": latency_ms,
                    "id": message_data.get("id")
                }
                
                await connection_info["ws"].send_text(json.dumps(response))
                print(f"Sent to {client_id}")
            except Exception as e:
                print(f"Error sending to {client_id}: {e}")
                # Handle disconnects might be done here or let the loop continue
        
        # 2. Publish to Redis for other workers (Scalability)
        if self.redis:
            try:
                # We publish the original message, workers will translate locally
                await self.redis.publish("chat_broadcast", json.dumps(message_data))
            except Exception as e:
                print(f"Redis publish failed: {e}")

    async def redis_listener(self):
        """
        Background task to listen for Redis messages and broadcast them locally.
        Should be started on app startup.
        """
        if not self.redis:
            return
        
        pubsub = self.redis.pubsub()
        await pubsub.subscribe("chat_broadcast")
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                # Broadcast locally (this will trigger translation for local clients)
                await self.broadcast(data)

manager = ConnectionManager()
