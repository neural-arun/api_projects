# Production AI Systems

## Reliability

AI systems are inherently probabilistic — the same input can produce different outputs.

| Challenge | Mitigation |
|---|---|
| LLM returns wrong answer | RAG with source requirements |
| LLM is down | Fallback to cached responses |
| LLM is slow | Streaming, smaller models for simple tasks |
| LLM costs money | Caching, semantic caching, batch processing |

## The Fallback Chain

Never assume the LLM is available:

```
def get_answer(question):
    # 1. Check cache first
    cached = cache.get(question)
    if cached: return cached
    
    # 2. Try primary LLM
    try:
        return call_primary_llm(question)
    except TimeoutError:
        pass  # Fall through
    
    # 3. Try backup LLM
    try:
        return call_backup_llm(question)
    except:
        pass  # Fall through
    
    # 4. Last resort — keyword search
    return search_database(question)
```

Each fallback is slightly worse but always available. User experience degrades gracefully.

## Latency Management

| Technique | Latency saved | Quality impact |
|---|---|---|
| Streaming (SSE) | Perceived 0ms (first token) | None |
| Smaller model | 50-80% | Some quality loss |
| Caching | 100% for cached queries | None |
| Batch processing | 60% (amortized) | Delayed responses |
| Early stopping | 30% | Lower quality |

For clinical ops, use streaming by default (Build 6). Cache common questions aggressively (Builds 7-8).

## Cost Management

LLM costs scale with token usage:

```
1 student asking 10 questions/day:
    10 questions × 500 input tokens × 200 output tokens
    = 7000 tokens/day ≈ $0.14/day (GPT-4)

1000 students × same:
    = 7M tokens/day ≈ $140/day
```

Strategies:
- Cache aggressively (many questions repeat)
- Use smaller models for simple queries
- Set max_tokens limits
- Monitor token usage per user/tenant

## Auditing & Compliance

Every AI action must be auditable:

```json
{
    "event_id": "evt_abc123",
    "timestamp": "2026-07-16T10:30:00Z",
    "user_id": "usr_456",
    "agent": "triage_agent",
    "action": "create_note",
    "input": "Patient reports chest pain",
    "output": "Created urgent note #789",
    "llm_call": {
        "model": "gpt-4",
        "prompt_tokens": 524,
        "completion_tokens": 128,
        "latency_ms": 2340,
        "cost": 0.0032
    },
    "human_review_required": true,
    "human_reviewed_at": null
}
```

## Gradual Rollout

New AI features should roll out gradually:

```
Phase 1: AI-only (prototype)
    → Agent runs, results logged but NOT shown to users

Phase 2: Shadow mode
    → Results shown to internal testers only

Phase 3: A/B test
    → 10% of users get AI features

Phase 4: Full rollout
    → All users, with kill switch
```

This pattern catches failures before they impact patients.

## Key Insight

A production AI system is not about the AI — it's about the **infrastructure around the AI**. Caching, fallbacks, monitoring, auditing, gradual rollout — these are what make AI reliable enough for healthcare. The LLM is just a component in a larger, carefully designed system.
