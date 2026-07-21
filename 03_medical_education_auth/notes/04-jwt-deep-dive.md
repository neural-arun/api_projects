# JWT Deep Dive

## What is JWT?

**JSON Web Token** — a way to encode a JSON object into a compact, URL-safe string that can be verified as authentic.

A JWT looks like:

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhcnVuIiwicm9sZSI6InN0dWRlbnQifQ.abc123signature
```

It has three parts separated by dots. The three parts are **header.payload.signature**.

## JWT Structure

```
┌─────────────────────────────────────────────────────────────┐
│                         JWT                                  │
├───────────────┬──────────────────────┬──────────────────────┤
│    HEADER     │      PAYLOAD         │     SIGNATURE        │
├───────────────┼──────────────────────┼──────────────────────┤
│ Algorithm     │ Claims (data):       │ Verifies token       │
│ & token type  │ - sub (user id)      │ wasn't tampered with │
│               │ - exp (expiry)       │                      │
│               │ - role               │                      │
│               │ - iat (issued at)    │                      │
└───────────────┴──────────────────────┴──────────────────────┘
```

**Important:** The payload is NOT encrypted. Anyone can decode a JWT and read its contents. The signature just verifies that the content hasn't been modified after issuance.

## Why JWT?

| Feature | JWT | Session (old way) |
|---|---|---|
| Storage | Client stores it | Server stores it |
| Scaling | Any server can verify it | Need shared session store (Redis) |
| Size | Larger (but still small) | Tiny (just a session ID) |
| Revocation | Hard (token valid until expiry) | Easy (delete session) |
| Payload | Contains user data | Just a reference ID |

**The key insight:** JWTs are **stateless**. The server doesn't need to look up anything — it just verifies the signature. This makes horizontal scaling trivial.

## The SECRET_KEY

The token is signed using a secret key known only to the server:

```
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
```

Generate one with: `openssl rand -hex 32`

- Anyone with the SECRET_KEY can forge tokens
- Store it in environment variables, never in code
- Rotate it if compromised

## Token Expiry

Every JWT should have a short expiry:

```
{
  "sub": "arun",
  "role": "student",
  "exp": 1712345678,        ← Expires (timestamp)
  "iat": 1712343878          ← Issued at (timestamp)
}
```

Common expiry times:
- Access token: 15–30 minutes
- Refresh token: 7–30 days

If an access token is stolen, it's only useful for 30 minutes. This limits damage.

## The Algorithm

We use **HS256** (HMAC with SHA-256):
- Symmetric — same key signs and verifies
- Fast and simple
- Good for a single server or trusted cluster

Production alternatives: RS256 (asymmetric, private key signs, public key verifies).

## What Happens on Every Request

```
Protected Request comes in
    │
    ▼
Extract token from Authorization header
    │
    ▼
Base64 decode the payload (NOT encrypted!)
    │
    ▼
Verify signature using SECRET_KEY
    │
    ▼
Check exp — is token still valid?
    │
    ▼
Extract sub (user identifier)
    │
    ▼
Fetch user from database
    │
    ▼
Pass user object to route
```

The signature verification prevents the client from modifying the payload (e.g., changing role to "admin").

## Caveats

**You can't revoke a JWT** (before expiry) without a blocklist. If a student is expelled, their token is still valid until it expires. Solutions:
- Keep access tokens short-lived (15 min)
- Use a Redis blocklist for immediate revocation (adds state)
- Rotate the SECRET_KEY in emergencies
