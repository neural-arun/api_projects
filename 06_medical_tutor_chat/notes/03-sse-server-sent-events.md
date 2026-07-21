# SSE — Server-Sent Events

## What Is SSE?

**Server-Sent Events** let a server push data to the client over a single long-lived HTTP connection. Data flows **one way**: server → client.

```
Client ──GET /stream──→ Server ──data──→ Client
                         ──data──→ Client
                         ──data──→ Client  (keeps sending)
```

The client opens a regular HTTP connection and the server keeps writing to it.

## SSE vs WebSockets

| Feature | SSE | WebSockets |
|---|---|---|
| Direction | Server → Client only | Bidirectional |
| Protocol | Plain HTTP | ws:// or wss:// |
| Auto-reconnect | Built-in (EventSource) | Manual |
| Browser support | Excellent | Excellent |
| Binary data | No (text only) | Yes |
| Use case | Streaming output | Chat, games |

For our medical tutor: use **WebSocket** for the chat input (student sends question), use **SSE** for the AI response streaming (server pushes tokens).

## SSE With FastAPI

FastAPI supports SSE through `StreamingResponse`:

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

async def event_generator():
    tokens = ["The", "heart", "has", "four", "chambers", "."]
    for token in tokens:
        yield f"data: {token}\n\n"
        await asyncio.sleep(0.3)

@app.get("/tutor/stream")
async def stream_tutor_response():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

The SSE format is simple:

```
data: The
data: heart
data: has
data: four
data: chambers
data: .
```

Each message is `data: <content>\n\n`. Two newlines separate events.

## Client-Side EventSource

```javascript
const eventSource = new EventSource("/tutor/stream");

eventSource.onmessage = (event) => {
    console.log("New token:", event.data);
    // Append to chat UI
};

eventSource.onerror = (err) => {
    console.log("Connection error, auto-reconnecting...");
};
```

`EventSource` **automatically reconnects** if the connection drops. No extra code needed.

## Use Case: Streaming AI Tutor Responses

When a student asks "What is systole?", the AI takes 3 seconds to generate an answer. Without streaming:

- Student waits 3 seconds in silence → bad UX

With SSE streaming:

- Student sees words appear as the AI generates them → feels like a real tutor

```python
async def stream_ai_response(question: str):
    # Simulate AI generating tokens
    full_response = get_ai_response(question)
    for token in full_response.split(" "):
        yield f"data: {token}\n\n"
        await asyncio.sleep(0.1)  # simulate generation delay
```

## Healthcare Analogy

- **Regular HTTP** = doctor writes full prescription, hands it to patient
- **SSE** = doctor dictates notes as they examine — nurse hears each word in real-time
- **Auto-reconnect** = if the dictation microphone glitches, it reconnects and keeps going

## Reference

- FastAPI docs: https://fastapi.tiangolo.com/tutorial/server-sent-events/
- MDN EventSource: https://developer.mozilla.org/en-US/docs/Web/API/EventSource
