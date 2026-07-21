# Real-Time Communication

## Why Real-Time?

A medical tutor needs to respond **instantly**. A student asks a question and waits:

- **Without real-time:** Student types → clicks Submit → waits for HTTP response → reads answer
- **With real-time:** Student types → answer appears character by character as the AI generates it

Real-time isn't a nice-to-have — it mimics a real tutor sitting beside the student.

## The Problem With HTTP

HTTP is **request-response**:

```
Student → HTTP Request → Server → HTTP Response → Student
          └── connection closes ──┘
```

Every interaction opens a new connection. For a chat with 30 back-and-forth messages, that's 30 separate HTTP connections.

## Three Approaches to Real-Time

| Approach | Direction | Best For |
|---|---|---|
| **Polling** | Client → Server (repeated) | Simple updates, legacy systems |
| **WebSockets** | Full-duplex (both ways) | Chat, live collaboration |
| **SSE** | Server → Client only | Streaming AI output, notifications |

### Polling (The Naive Way)

```python
# Client asks every 2 seconds: "any new messages?"
# Server responds even if nothing changed
@app.get("/poll/{session_id}")
def poll_messages(session_id: str):
    return {"messages": get_new_messages(session_id)}
```

**Problems:** Wasteful — most polls return nothing. Latency — worst case 2s delay. Scales badly.

### WebSockets (Full-Duplex)

```
Student ←→ WebSocket ←→ Server
```

Both sides send messages whenever they want. No polling. One persistent connection.

**Use cases:** Chat where both sides type, collaborative note editing, live vitals monitoring.

### SSE (Server-Sent Events)

```
Student → HTTP GET → Server ──stream of events──→ Student
```

Server pushes data to the client. Client cannot send data over the same connection (needs separate HTTP for that).

**Use cases:** AI streaming responses, live alerts, news tickers.

## Healthcare Analogy

- **HTTP** is like calling a receptionist — you ask, they go check, come back with answer, hang up
- **Polling** is like calling every 10 seconds to ask "is the doctor ready yet?"
- **WebSockets** is like an open phone line — both sides talk freely
- **SSE** is like a PA system — hospital announces, everyone listens

## Decision Flow

```
Do you need two-way communication?
  ├── Yes → WebSockets
  └── No → Do you need to stream data continuously?
       ├── Yes → SSE
       └── No → Regular HTTP is fine
```

For our medical tutor: we use **WebSockets** for the chat itself (student types, tutor responds), and **SSE** for streaming the AI's response token by token.
