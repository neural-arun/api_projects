# Chat Session Management

## The Problem

A medical tutor conversation is **contextual**. A student asks:

1. "What is the cardiac cycle?"
2. "What happens during systole?"  (refers back to #1)

Without session management, the tutor treats each question in isolation. The second question loses context.

## Session IDs

Each chat gets a unique ID. The server stores all messages for that session:

```python
from pydantic import BaseModel
from datetime import datetime

class ChatSession(BaseModel):
    session_id: str
    student_name: str
    created_at: datetime
    messages: list["ChatMessage"]

class ChatMessage(BaseModel):
    role: str  # "student" or "tutor"
    content: str
    timestamp: datetime
```

**Database model:**

```python
from sqlmodel import SQLModel, Field

class ChatSessionDB(SQLModel, table=True):
    session_id: str = Field(primary_key=True)
    student_name: str
    created_at: datetime

class ChatMessageDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="chatsessiondb.session_id")
    role: str
    content: str
    timestamp: datetime
```

## Full Chat Flow

```
Student                      Server                       AI Model
  │                            │                            │
  │── WebSocket connect ──────→│                            │
  │                            │── create session ─────────→│
  │← session_id ──────────────│                            │
  │── question ──────────────→│                            │
  │                            │── lookup history ────────→│
  │                            │── build context prompt ──→│
  │                            │← start streaming ─────────│
  │← SSE: token ──────────────│                            │
  │← SSE: token ──────────────│                            │
  │← SSE: token ──────────────│                            │
  │← SSE: done ──────────────│                            │
  │                            │── store Q&A ─────────────→│
```

## Context Window Management

AI models have a **context window** limit (e.g., 4096 tokens for GPT-3.5). The full chat history may not fit.

**Strategy — Sliding Window:**

```python
MAX_TOKENS = 3000  # reserve 1000 for the response

def build_context(messages: list[ChatMessage], max_tokens: int):
    context = []
    token_count = 0

    # Start from most recent, go backwards
    for msg in reversed(messages):
        tokens = estimate_tokens(msg.content)
        if token_count + tokens > max_tokens:
            break
        context.insert(0, msg)
        token_count += tokens

    return context
```

This keeps only the most recent messages that fit within the context limit.

## Combining WebSocket + SSE

A common pattern: WebSocket for the chat, SSE for streaming output.

```python
@app.websocket("/chat/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()

    while True:
        question = await websocket.receive_text()

        # Store student's question
        store_message(session_id, "student", question)

        # Get context from history
        history = get_chat_history(session_id)
        context = build_context(history)

        # Stream AI response via SSE endpoint
        async for token in stream_ai_response(question, context):
            await websocket.send_json({"type": "token", "data": token})

        # Store complete response
        store_message(session_id, "tutor", full_response)
```

## Healthcare Analogy

- **Session** = a patient's visit to the doctor
- **History** = medical records — doctor reviews them before treating
- **Context window** = doctor's memory — they can only recall so many details at once
- **Sliding window** = doctor focuses on most recent symptoms, not the patient's entire life

## Reference

- SQLModel docs: https://sqlmodel.tiangolo.com/
- OpenAI context limits: https://platform.openai.com/docs/models/gpt-4
