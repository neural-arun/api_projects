# Build 6 — Medical Tutor Chat Backend — Notes Index

Read these in order. Each builds on the previous one.

| # | Note | What You'll Learn |
|---|---|---|
| 01 | `01-real-time-communication.md` | Polling vs WebSockets vs SSE — tradeoffs |
| 02 | `02-websockets-in-fastapi.md` | WebSocket endpoints, ConnectionManager |
| 03 | `03-sse-server-sent-events.md` | SSE with StreamingResponse, EventSource |
| 04 | `04-streaming-responses.md` | Streaming AI responses token by token |
| 05 | `05-chat-session-management.md` | Chat history, session IDs, context windows |
| 06 | `06-async-concurrency-deep-dive.md` | Async/await, event loop, tasks, futures |

## Prerequisites

- Build 1 completed (FastAPI routes, Pydantic, HTTP)
- Build 2 completed (SQLModel, database sessions)
- Basic understanding of `async/await` in Python

## What You're Building

```
Medical Tutor Chat Backend

Features:
- Real-time chat via WebSockets
- Streaming AI tutor responses via SSE
- Chat session management with history
- Concurrent handling of multiple students
- Token-by-token response streaming
```

Each feature introduces a real-time pattern used in healthcare: live guidance during procedures, instant triage answers, streaming AI-generated explanations.

## How To Use

1. Read notes in order
2. Type out code examples yourself
3. After reading all notes, build the Medical Tutor Chat from scratch
4. Refer back when stuck

## Official References

- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [FastAPI Server-Sent Events](https://fastapi.tiangolo.com/tutorial/server-sent-events/)
- [FastAPI Streaming Data](https://fastapi.tiangolo.com/advanced/stream-data/)
- [FastAPI Async](https://fastapi.tiangolo.com/async/)
- [Python `asyncio` docs](https://docs.python.org/3/library/asyncio.html)
