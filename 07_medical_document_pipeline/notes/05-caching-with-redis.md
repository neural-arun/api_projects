# Caching with Redis

## Why Cache?

Reading from a database is fast (~10ms). Reading from Redis is faster (~1ms). But the real win is reducing database load for repeated queries.

```
Without cache:          With cache:
GET /patients/42        GET /patients/42
    │                        │
    ▼                        ▼
  DB query (10ms)        Redis check (1ms)
    │                        ├── Hit → return cached
    ▼                        └── Miss → DB → store in cache
  Return JSON                      → return
```

If the same data is requested 100 times, without cache you hit the DB 100 times. With cache, you hit the DB once.

## Cache-Aside Pattern

The most common caching pattern:

```
def get_patient(patient_id):
    # 1. Try cache first
    cached = redis.get(f"patient:{patient_id}")
    if cached:
        return json.loads(cached)

    # 2. Cache miss — query database
    patient = db.query(Patient).get(patient_id)

    # 3. Store in cache for next time
    redis.setex(f"patient:{patient_id}", 3600, patient.json())
    #                                    ^^^^ expires in 1 hour

    return patient
```

## Cache Invalidation

The hardest problem in computer science: **when to invalidate cache?**

When data changes (UPDATE, DELETE), the cached version becomes stale.

```
def update_patient(patient_id, data):
    # Update database
    patient = db.query(Patient).get(patient_id)
    patient.name = data.name
    db.commit()

    # Invalidate cache
    redis.delete(f"patient:{patient_id}")
    # Next request will miss cache, fetch fresh data, and re-cache
```

Strategies:
| Strategy | How it works | Risk |
|---|---|---|
| TTL (time-to-live) | Cache expires automatically after N seconds | Stale data within TTL window |
| Write-through | Update cache when DB updates | Consistent, but more writes |
| Cache invalidation | Delete cache key on update | May miss some updates |

## What to Cache

| Good to cache | Bad to cache |
|---|---|
| Patient details (rarely change) | Real-time vitals monitor |
| Course content (static) | Search results (highly variable) |
| AI model inferences (same input → same output) | User-specific dashboards |
| Reference data (medications list) | Audit logs |

## Redis as Session Store

In Build 3, we mentioned tokens are stateless. But if you need server-side sessions (e.g., for WebSocket chats):

```
# On login
session_id = str(uuid4())
redis.setex(f"session:{session_id}", 86400, user_id)
# Stores: "session:abc123" → "42" (user id), expires in 24h

# On each request
user_id = redis.get(f"session:{session_id}")
```

This lets any server instance validate sessions — essential for horizontal scaling.

## When NOT to Cache

- Data that changes every second (stock prices, live vitals)
- User-specific data that's rarely repeated
- Small datasets that are already fast to query
- Operations that must be 100% up-to-date (financial transactions)

## Key Insight

Caching is a **performance optimization**, not a correctness mechanism. The system must work correctly without the cache. The cache just makes it faster.
