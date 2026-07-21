# OAuth2 & Bearer Tokens

## What is OAuth2?

OAuth2 is a **specification** that defines how authorization works on the web. It has several "flows" for different scenarios.

For our API, we use the **Password Flow**:
1. Client sends username + password to a single endpoint
2. Server validates and returns a token
3. Client sends that token with every subsequent request

## Bearer Tokens

A "Bearer" token means: "Whoever bears (holds) this token is the authorized user."

The client sends it as an HTTP header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

The server reads this header on every protected request.

## How OAuth2PasswordBearer Works

FastAPI provides a built-in tool:

```
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
```

This does:
1. Tells FastAPI that this endpoint uses Bearer token auth
2. Tells the /docs UI to show a "Authorize" button
3. Automatically extracts the token from the Authorization header
4. Returns the token string to your dependency function

## The Token Endpoint Flow

```
Client                          Server
  │                               │
  │  POST /token                  │
  │  body: username=arun&         │
  │        password=secret        │
  │──────────────────────────────>│
  │                               │── Look up user in DB
  │                               │── Verify password hash
  │                               │── Generate token
  │                               │
  │  200 OK                       │
  │  {"access_token": "eyJ...",   │
  │   "token_type": "bearer"}     │
  │<──────────────────────────────│
  │                               │
  │  GET /courses                 │
  │  Authorization: Bearer eyJ... │
  │──────────────────────────────>│
  │                               │── Decode & verify token
  │                               │── Return courses
```

## The Password Flow vs. Full OAuth2

| Aspect | Our approach | Full OAuth2 |
|---|---|---|
| User enters credentials | In our app | On Google/Facebook page |
| We store passwords | Yes | No (Google stores them) |
| Complexity | Low | High |
| Use case | Our own users | Social login |

What we implement is often called "OAuth2 with Password Flow" — it's OAuth2's simplest flow, designed for first-party apps.

## The Dependency Chain

```
Protected Route
    └── Depends(get_current_active_user)
            └── Depends(get_current_user)
                    └── Depends(oauth2_scheme)  ← Extracts token
```

Each layer adds a check:
1. `oauth2_scheme` — extracts the raw token string
2. `get_current_user` — decodes token, fetches user from DB
3. `get_current_active_user` — checks if user account is active/disabled

## Why This Pattern Matters

This separation means:
- You can protect individual routes, groups, or the whole app
- Dependencies compose — mix and match checks
- Tests can override individual dependencies
- The interface is clean — route functions just get a user object
