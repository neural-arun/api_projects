# WebSockets in FastAPI

## What Is a WebSocket?

A **WebSocket** is a persistent, bidirectional connection between client and server. Unlike HTTP where the client always initiates, WebSockets let either side send data at any time.

```
HTTP:   Client ──request──→ Server ──response──→ Client  (done)
WebSocket: Client ←─────────────────────────────→ Server  (stays open)
```

## WebSocket Endpoint in FastAPI

```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
```

| Step | Code | What Happens |
|---|---|---|
| 1 | `@app.websocket("/ws")` | Route accepts WebSocket connections |
| 2 | `await websocket.accept()` | Server agrees to upgrade connection |
| 3 | `await websocket.receive_text()` | Wait for a text message from client |
| 4 | `await websocket.send_text(...)` | Send a text message back |
| 5 | loop back to step 3 | Keep the conversation going |

## Client-Side JavaScript

```javascript
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onopen = () => ws.send("Hello tutor!");

ws.onmessage = (event) => {
    console.log("Tutor says:", event.data);
};

ws.onclose = () => console.log("Connection closed");
```

## Handling Multiple Clients — ConnectionManager

A simple echo server is useless. We need to track many students:

```python
from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{student_id}")
async def chat_endpoint(websocket: WebSocket, student_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            response = f"Tutor to {student_id}: {data}"
            await manager.broadcast(response)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

## Disconnection Handling

When a client closes their browser, the server must handle the broken connection. FastAPI raises `WebSocketDisconnect`:

```python
from fastapi import WebSocketDisconnect

try:
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"You said: {data}")
except WebSocketDisconnect:
    print("Client disconnected")
    manager.disconnect(websocket)
```

Without this try/except, a disconnect crashes the entire endpoint.

## The `websockets` Library Requirement

FastAPI's WebSocket support depends on the `websockets` library:

```bash
pip install websockets
```

Without it, `@app.websocket()` raises an import error at startup.

## Healthcare Analogy

- **WebSocket connection** = an open video call between student and tutor
- **`accept()`** = tutor picks up the call
- **`receive_text()`** = tutor hears the student speak
- **`send_text()`** = tutor responds
- **`WebSocketDisconnect`** = student hangs up, tutor stops talking
- **ConnectionManager** = call center that tracks all active calls

## Reference

- FastAPI docs: https://fastapi.tiangolo.com/advanced/websockets/
- `websockets` library: https://websockets.readthedocs.io/
