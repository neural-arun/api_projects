# Build 6 — Medical Tutor Chat — Quiz

Mark each answer. `[ ]` → `[x]`.

---

### Q1

What is the fundamental difference between HTTP and WebSockets?

- [ ] A) HTTP is faster
- [ ] B) HTTP is request-response; WebSockets are full-duplex
- [ ] C) WebSockets only work with JavaScript
- [ ] D) HTTP uses port 80, WebSockets use port 443

B

---

### Q2

Which FastAPI decorator creates a WebSocket endpoint?

- [ ] A) `@app.get("/ws")`
- [ ] B) `@app.ws("/ws")`
- [ ] C) `@app.websocket("/ws")`
- [ ] D) `@app.socket("/ws")`

C

---

### Q3

What does `websocket.accept()` do?

- [ ] A) Rejects the connection
- [ ] B) Sends a 101 Switching Protocols response, completing the handshake
- [ ] C) Opens a database connection
- [ ] D) Validates the client's API key

B

---

### Q4

What exception is raised when a WebSocket client disconnects?

- [ ] A) `ConnectionError`
- [ ] B) `WebSocketError`
- [ ] C) `WebSocketDisconnect`
- [ ] D) `DisconnectException`

C

---

### Q5

True or False: SSE allows the client to send messages to the server over the same connection.

- [ ] True
- [ ] False

False

---

### Q6

Which FastAPI class is used to implement SSE?

- [ ] A) `JSONResponse`
- [ ] B) `HTMLResponse`
- [ ] C) `StreamingResponse`
- [ ] D) `PlainTextResponse`

C

---

### Q7

What media type must be set for an SSE endpoint?

- [ ] A) `application/json`
- [ ] B) `text/html`
- [ ] C) `text/event-stream`
- [ ] D) `application/octet-stream`

C

---

### Q8

Which JavaScript API automatically reconnects on connection loss?

- [ ] A) `WebSocket`
- [ ] B) `fetch()`
- [ ] C) `EventSource`
- [ ] D) `XMLHttpRequest`

C

---

### Q9

True or False: StreamingResponse uses `Transfer-Encoding: chunked` so the server doesn't need to know the content length upfront.

- [ ] True
- [ ] False

True

---

### Q10

What does `asyncio.gather()` do?

- [ ] A) Runs coroutines sequentially
- [ ] B) Runs coroutines concurrently and waits for all to finish
- [ ] C) Cancels all running tasks
- [ ] D) Creates a new event loop

B

---

### Q11

Which of these blocks the event loop and should be avoided in async routes?

- [ ] A) `await asyncio.sleep(1)`
- [ ] B) `await websocket.receive_text()`
- [ ] C) `time.sleep(1)`
- [ ] D) `async for token in stream`

C

---

### Q12

You have chat messages: Q1, A1, Q2, A2, Q3. The AI context window fits only 3 messages.

Which strategy correctly builds context?

- [ ] A) Use the first 3 messages (Q1, A1, Q2)
- [ ] B) Use the most recent 3 messages (A1, Q2, A2)
- [ ] C) Use the most recent 3 messages that fit within the token limit
- [ ] D) Skip context entirely

C

---

### Q13

True or False: A WebSocket connection stays open after the server sends a response, unlike HTTP.

- [ ] True
- [ ] False

True

---

### Q14

What does `asyncio.to_thread()` do?

- [ ] A) Creates a new thread for an async function
- [ ] B) Runs a synchronous blocking function in a separate thread without blocking the event loop
- [ ] C) Starts a new Python process
- [ ] D) Converts a coroutine into a thread

B

---

### Q15

In a medical tutor chat, which pattern combines both WebSocket and SSE?

- [ ] A) WebSocket for question input, SSE for streaming the answer
- [ ] B) SSE for everything
- [ ] C) WebSocket for everything
- [ ] D) Polling with regular HTTP

A

---

**Answer Key:**

| Q | Answer | Note Reference |
|---|---|---|
| 1 | B | 01-real-time-communication.md |
| 2 | C | 02-websockets-in-fastapi.md |
| 3 | B | 02-websockets-in-fastapi.md |
| 4 | C | 02-websockets-in-fastapi.md |
| 5 | False | 03-sse-server-sent-events.md |
| 6 | C | 03-sse-server-sent-events.md |
| 7 | C | 03-sse-server-sent-events.md |
| 8 | C | 03-sse-server-sent-events.md |
| 9 | True | 04-streaming-responses.md |
| 10 | B | 06-async-concurrency-deep-dive.md |
| 11 | C | 06-async-concurrency-deep-dive.md |
| 12 | C | 05-chat-session-management.md |
| 13 | True | 02-websockets-in-fastapi.md |
| 14 | B | 06-async-concurrency-deep-dive.md |
| 15 | A | 05-chat-session-management.md |
