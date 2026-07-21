# Streaming Responses

## The Problem

A medical tutor generates long, detailed answers. If the server waits until the full response is ready, the student stares at a blank screen.

**Without streaming:**
```
Student sends question → Server thinks for 5s → Returns full text → Student reads
```

**With streaming:**
```
Student sends question → Server sends "The" → "...heart" → "...pumps" → "...blood" (student reads as it arrives)
```

## StreamingResponse

`StreamingResponse` wraps an **async generator** — a function that `yield`s chunks instead of `return`ing one value:

```python
from fastapi.responses import StreamingResponse
import asyncio

async def generate_answer():
    tokens = ["Systole", "is", "the", "phase", "of", "the", "cardiac", "cycle"]
    for token in tokens:
        yield token + " "
        await asyncio.sleep(0.2)  # simulate AI generation

@app.get("/systole")
async def get_answer():
    return StreamingResponse(
        generate_answer(),
        media_type="text/plain"
    )
```

## `yield` vs `return` in Async Context

| | `return` | `yield` |
|---|---|---|
| Behavior | Returns one value, function ends | Returns multiple values, function pauses between them |
| Response type | Full body at once | Chunked, sent as available |
| Use case | Short fixed answers | Long generated answers |
| Memory | Whole response in memory | One chunk at a time |

## Chunked Transfer Encoding

When you use `StreamingResponse`, FastAPI automatically sets:

```
Transfer-Encoding: chunked
```

This tells the client: "I don't know the total length yet. I'll send pieces as they come."

Without chunked encoding, the server must know the full `Content-Length` before sending — which defeats the purpose of streaming.

## Use Case: AI-Powered Medical Tutor

```python
import openai  # hypothetical

async def stream_tutor_answer(question: str, session_history: list):
    # Build prompt with context
    messages = session_history + [{"role": "user", "content": question}]

    # Stream tokens from AI model
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=messages,
        stream=True  # enables token-by-token output
    )

    async for chunk in response:
        token = chunk.choices[0].delta.get("content", "")
        if token:
            yield token
```

The client receives each token immediately via SSE (`text/event-stream`) or plain streaming (`text/plain`).

## Combine With SSE for Structured Events

```python
async def stream_sse(question: str):
    tokens = await get_ai_tokens(question)
    full_response = ""

    async for token in tokens:
        full_response += token
        yield f"data: {json.dumps({'token': token, 'full': full_response})}\n\n"

    yield f"data: {json.dumps({'done': True})}\n\n"
```

## Healthcare Analogy

- **Regular response** = pharmacy fills entire prescription, then hands it over
- **Streaming response** = pharmacist hands you each medication as they pick it off the shelf
- **Chunked encoding** = the pharmacist saying "I don't know how many items you'll need — I'll pass them one at a time"

## Reference

- FastAPI docs: https://fastapi.tiangolo.com/advanced/stream-data/
- MDN Chunked transfer encoding: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding
