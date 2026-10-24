# 💬 Build 06 · Medical Tutor Chat Backend

> **Your build:** A student asks a medical-learning question and receives an answer as it is generated. The API keeps the chat session and message history.

**The journey:** Student question → tutor service → answer streams back → conversation is saved

---

## 🔌 01 · WebSockets vs SSE

**🧠 Concept** — A WebSocket keeps one connection open for messages in both directions. Server-Sent Events (SSE) stream events from server to client over HTTP; the client does not send messages back on that same stream.

**🩺 In Medical Tutor** — The student sends a question, then watches the tutor’s answer arrive piece by piece. The student may send a follow-up as a new request or over a WebSocket.

**🛠 Build it**

- Use **SSE** when the main need is streaming answer text to the student.
- Use **WebSockets** when both sides need to send live messages through one persistent connection.
- Start with SSE for a simple request-and-stream chat; use WebSockets if the product needs richer two-way events.

~~~text
SSE: student ─question→ API ─answer chunks→ student
WebSocket: student ⇄ API (messages both ways)
~~~

---

## 🌊 02 · Streaming responses

**🧠 Concept** — A normal response waits until the result is ready. A streaming response sends chunks as they become available.

**🩺 In Medical Tutor** — The student sees the answer appear progressively instead of waiting for the entire response.

**🛠 Build it** — Connect the tutor’s output stream to FastAPI’s StreamingResponse or SSE support. Send a clear start, content chunks, and end/error signal; stop work if the client disconnects.

~~~text
Tutor generates
├── chunk 1 → send
├── chunk 2 → send
└── final chunk → finish
~~~

---

## ⚡ 03 · Async & concurrency

**🧠 Concept** — Async lets a server work on another request while one request is waiting for network or model output. It helps with waiting-heavy I/O; it does not make heavy CPU work automatically faster.

**🩺 In Medical Tutor** — Many students may wait on model responses at the same time.

**🛠 Build it** — Use async-compatible model and network clients. Set timeouts and limits, handle disconnects, and avoid blocking the event loop with slow synchronous work.

~~~text
Student A waits for tutor ─┐
Student B receives chunks  ├─ server handles concurrent I/O
Student C starts question ─┘
~~~

---

## 🗂️ 04 · Sessions & message history

**🧠 Concept** — A session groups messages into one conversation. History gives the tutor context from earlier messages.

**🩺 In Medical Tutor** — A follow-up like “why?” should be connected to the student’s previous question.

**🛠 Build it** — Give each conversation a session ID, store ordered messages, and send only the relevant history to the tutor. Set retention and access rules because questions may contain sensitive information. Keep educational answers clearly separate from clinical diagnosis.

~~~text
Session
├── student + access rules
├── ordered messages
└── context for next answer
~~~

### 📚 Official references

- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [FastAPI Server-Sent Events](https://fastapi.tiangolo.com/tutorial/server-sent-events/)
- [FastAPI streaming responses](https://fastapi.tiangolo.com/advanced/custom-response/)
- [FastAPI async and await](https://fastapi.tiangolo.com/async/)
