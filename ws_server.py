from fastapi import FastAPI, WebSocket
from typing import List
import uvicorn
import json

app = FastAPI()

# List to store active WebSocket connections
connected_clients: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received: {data}")
    except Exception as e:
        print(e)
    finally:
        connected_clients.remove(websocket)

# Function to send a JSON message to all connected clients
async def send_message_to_clients(message: dict):
    for client in connected_clients:
        try:
            await client.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending message: {e}")

# Example endpoint to trigger message sending
@app.get("/send-message")
async def trigger_message(message: dict):
    await send_message_to_clients(message)
    return message


if __name__ == "__main__":
    uvicorn.run("ws_server:app", port=8000, log_level="info")
