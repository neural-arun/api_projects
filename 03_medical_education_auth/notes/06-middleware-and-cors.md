# Middleware & CORS

## What is Middleware?

Middleware is code that runs on **every request**, before and after your route handler.

```
Request → Middleware → Router → Route → Response → Middleware → Client
              ▲                                         │
              └───────── process time, logging ──────────┘
```

Think of it as a checklist that every request must pass through.

## Common Middleware Uses

| Use case | What it does |
|---|---|
| Process time | Log how long each request took |
| Request logging | Log every request for auditing |
| CORS headers | Allow frontend from different origin |
| Rate limiting | Block excessive requests |
| Security headers | Add HSTS, CSP headers |
| Compression | Gzip responses |

## Middleware in FastAPI

```
@app.middleware("http")
async def add_process_time(request, call_next):
    # Code before route (pre-processing)
    start = time.now()
    
    response = await call_next(request)  # ← Request goes to route
    
    # Code after route (post-processing)
    elapsed = time.now() - start
    response.headers["X-Process-Time"] = str(elapsed)
    
    return response
```

The `call_next` function is the bridge. Everything before it runs on the request in, everything after runs on the response out.

## CORS — Cross-Origin Resource Sharing

### The Problem

A browser running at `http://localhost:5173` (React/Vue dev server) trying to call your API at `http://localhost:8000`.

The browser blocks this because they're different **origins**:

```
http://localhost:5173  ≠  http://localhost:8000
(different ports = different origins)
```

### The Solution

Your API must explicitly tell the browser: "I allow requests from that origin."

This is done via HTTP headers:

```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Allow-Credentials: true
```

### Setting up CORSMiddleware

```
origins = [
    "http://localhost:5173",    // React dev
    "http://localhost:3000",    // Next.js dev
    "https://myapp.com",        // Production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Don't use `allow_origins=["*"]` in production — it blocks credentialed requests (cookies, auth headers).

## CORS Preflight

For "non-simple" requests (POST with JSON, custom headers like Authorization), the browser first sends an **OPTIONS** request to check if the actual request is allowed:

```
Browser                    Server
  │                          │
  │  OPTIONS /courses        │
  │  Origin: localhost:5173  │
  │─────────────────────────>│
  │                          │── Check if origin is allowed
  │  200 OK                  │
  │  Access-Control-*        │
  │<─────────────────────────│
  │                          │
  │  GET /courses            │  (Now the real request)
  │  Authorization: Bearer.. │
  │─────────────────────────>│
```

## Middleware vs Dependencies

Both run before routes. When to use what:

| | Middleware | Dependencies |
|---|---|---|
| Scope | Every request | Selected routes |
| Can modify response | ✅ | ❌ (limited) |
| Can abort request | ✅ | ✅ |
| Access to route context | ❌ | ✅ (path params, etc.) |
| Use for | Logging, CORS, headers | Auth, DB sessions, permissions |

**The rule:** Use middleware for infrastructure concerns (CORS, logging). Use dependencies for application concerns (auth, permissions, DB).

## Putting It Together

In production:
1. CORS middleware — allows frontend to call API
2. Logging middleware — records every request
3. Auth dependencies — protect sensitive routes
4. Role dependencies — enforce permissions
