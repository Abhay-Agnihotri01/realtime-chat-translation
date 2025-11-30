import asyncio
import websockets
import sys

async def test_connection():
    uri = "ws://localhost:8000/ws/user_test"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected successfully!")
            await websocket.send('{"content": "Hello", "target_lang": "es"}')
            response = await websocket.recv()
            print(f"Received: {response}")
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"Failed with status code: {e.status_code}")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e.code} - {e.reason}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
