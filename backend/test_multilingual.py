import asyncio
import websockets
import json
import sys

async def client_receiver():
    uri = "ws://127.0.0.1:8000/ws/user_receiver?lang=spa_Latn"
    async with websockets.connect(uri) as websocket:
        print("Receiver (Spanish) connected")
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            data = json.loads(message)
            print(f"Receiver got: {data['translated']}")
            if "Hola" in data['translated']:
                print("SUCCESS: Translation received correctly")
            else:
                print(f"FAILURE: Unexpected translation: {data['translated']}")
        except asyncio.TimeoutError:
            print("FAILURE: Timed out waiting for message")

async def client_sender():
    uri = "ws://127.0.0.1:8000/ws/user_sender?lang=eng_Latn"
    # Wait a bit for receiver to connect
    await asyncio.sleep(2)
    async with websockets.connect(uri) as websocket:
        print("Sender (English) connected")
        msg = {
            "content": "Hello",
            # target_lang is ignored by backend now, it uses receiver's preference
        }
        await websocket.send(json.dumps(msg))
        print("Sender sent: Hello")

async def main():
    # Run both clients concurrently
    await asyncio.gather(client_receiver(), client_sender())

if __name__ == "__main__":
    asyncio.run(main())
