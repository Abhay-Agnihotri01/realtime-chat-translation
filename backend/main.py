from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
import time
import asyncio
from socket_manager import manager
from privacy_service import privacy_service
try:
    from evaluation import evaluator
    EVALUATION_ENABLED = True
except ImportError:
    EVALUATION_ENABLED = False
    print("Warning: Evaluation module not available")
# from .translation_service import TranslationService # Lazy load to avoid startup delay during install

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global translation service instance (lazy loaded)
translation_service = None

def get_translation_service():
    global translation_service
    if translation_service is None:
        from translation_service import TranslationService
        translation_service = TranslationService()
    return translation_service

    return translation_service

async def get_translation_service_async():
    global translation_service
    if translation_service is None:
        loop = asyncio.get_event_loop()
        from translation_service import TranslationService
        # Run in executor to avoid blocking the event loop during model load
        translation_service = await loop.run_in_executor(None, TranslationService)
    return translation_service

def is_model_loaded():
    return translation_service is not None

@app.on_event("startup")
async def startup_event():
    # Start Redis listener in background
    # asyncio.create_task(manager.redis_listener())
    pass # Commented out for MVP if Redis is not installed, to avoid errors.
    # If Redis IS installed, uncomment above.

# @app.get("/")
# async def root():
#     return {"message": "Real-Time Multilingual Chat Translation API is running"}

@app.get("/metrics")
async def get_metrics():
    """Get system performance metrics"""
    if EVALUATION_ENABLED:
        return {
            "performance_report": evaluator.generate_performance_report(),
            "total_translations": len(evaluator.latency_history),
            "active_connections": len(manager.active_connections)
        }
    else:
        return {
            "performance_report": "Evaluation module not available",
            "total_translations": 0,
            "active_connections": len(manager.active_connections)
        }

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    if EVALUATION_ENABLED:
        avg_latency = sum(evaluator.latency_history[-10:]) / min(10, len(evaluator.latency_history)) if evaluator.latency_history else 0
        return {
            "status": "healthy" if avg_latency < 500 else "degraded",
            "avg_latency_ms": avg_latency,
            "active_connections": len(manager.active_connections)
        }
    else:
        return {
            "status": "healthy",
            "avg_latency_ms": 0,
            "active_connections": len(manager.active_connections)
        }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, lang: str = "eng_Latn"):
    await manager.connect(websocket, client_id, lang)
    
    # Notify others that user joined
    join_msg = {
        "content": f"Client #{client_id} joined",
        "sender": "System",
        "original_lang": "eng_Latn",
        "id": str(time.time())
    }
    await manager.broadcast(join_msg, exclude_client_id=client_id)

    try:
        while True:
            data = await websocket.receive_text()
            # Expecting JSON: {"content": "Hello", "target_lang": "spa_Latn"}
            # For MVP, we might just receive text and assume a default target or parse it.
            
            # Let's assume the client sends a JSON string
            try:
                message_data = json.loads(data)
                content = message_data.get("content")
                # target_lang is now determined by the receiver's preference, not the sender
            except json.JSONDecodeError:
                # Fallback for plain text
                content = data

            # Privacy: Sanitize message content
            content = privacy_service.sanitize_message(content)
            anonymized_client_id = privacy_service.anonymize_user_id(client_id)
            
            # Prepare message for broadcast
            broadcast_data = {
                "content": content,
                "sender": anonymized_client_id,
                "original_lang": lang, # The sender's language
                "id": str(time.time()) # Simple ID
            }
            
            print(f"Received from {client_id}: {content}. Broadcasting...")
            # Broadcast to all (manager handles individual translation)
            await manager.broadcast(broadcast_data, exclude_client_id=client_id)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id, websocket)
        disconnect_msg = {
            "content": f"Client #{client_id} left",
            "sender": "System",
            "original_lang": "eng_Latn",
            "id": str(time.time())
        }
        await manager.broadcast(disconnect_msg)
