# Why Authentication Matters

## The Core Problem

HTTP is **stateless**. Every request is independent — the server forgets you the moment it sends the response.

```
Request 1:  GET /patients        → "Who are you?"
Request 2:  GET /patients        → "Who are you? (again?)"
```

Without auth, anyone can access anything. In a medical education platform, that means:
- A student could access admin panels
- A competitor could scrape all course content
- Patient data (even simulated) could leak

## Authentication vs Authorization

| Concept | Question it answers | Example |
|---|---|---|
| Authentication | Who are you? | "I am arun, here's my password" |
| Authorization | What can you do? | "Arun is a student, so he can view courses but not edit them" |

Auth **comes first**. The server must identify you before it can decide what you're allowed to do.

## The Auth Flow (Systems View)

```
                    ┌─────────────────┐
                    │  Client (browser)│
                    └────────┬────────┘
                             │ 
                    POST /login with credentials
                             │
                             ▼
                    ┌─────────────────┐
                    │  Server checks   │
                    │  credentials     │──→ Wrong → 401 Unauthorized
                    │  (password hash) │
                    └────────┬────────┘
                             │ Correct
                             ▼
                    ┌─────────────────┐
                    │  Server issues   │
                    │  a token (JWT)   │──→ Returned to client
                    └─────────────────┘
                             │
                    Subsequent requests include token
                             │
                             ▼
                    ┌─────────────────┐
                    │  Server verifies │
                    │  token on every  │──→ Valid → process request
                    │  request         │──→ Invalid → 401
                    └─────────────────┘
```

## Common Auth Methods

| Method | How it works | When to use |
|---|---|---|
| API Key | Static key in header | Machine-to-machine, simple |
| Basic Auth | username:password in base64 | Legacy, avoid |
| Bearer Token (JWT) | Signed token in header | Most web APIs — what we build |
| OAuth2 (full) | Third-party login (Google, etc.) | When users login via external providers |

## Healthcare Context

Medical data has legal protections (HIPAA in US, DPDP in India). Even in a learning platform, you must:
- Never expose patient data to unauthorized roles
- Log all access to sensitive data
- Expire sessions aggressively
- Use HTTPS everywhere (tokens sent in every request!)

## What You Should Ask Yourself

- If someone steals a token, what damage can they do before it expires?
- If a student graduates, how do you revoke their access?
- If the database is stolen, are passwords exposed?
