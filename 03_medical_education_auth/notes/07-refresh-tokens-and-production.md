# Refresh Tokens & Production Security

## The Token Dilemma

Short-lived access tokens (15 min) are secure but annoying — users must login every 15 minutes.

Long-lived access tokens (30 days) are convenient but dangerous — stolen tokens work for 30 days.

**Solution:** Two tokens — a short access token and a long refresh token.

## The Two-Token System

```
Login
    │
    ▼
Server returns:
├── access_token  (15 min)  → Used for API calls
└── refresh_token (7 days)  → Used ONLY to get new access tokens
```

```
Access Token expires
    │
    ▼
Client sends refresh_token to /refresh
    │
    ▼
Server validates refresh_token
    │
    ▼
Server issues NEW access_token (and optionally new refresh_token)
```

## Token Storage

| Storage | Accessible by JavaScript | Risk |
|---|---|---|
| localStorage | ✅ Yes | XSS attacks can steal tokens |
| HTTP-only cookie | ❌ No | CSRF attacks possible |
| Memory (variable) | ❌ No | Lost on page refresh |

**Best practice for web apps:**
- Access token in memory (lost on refresh, short-lived anyway)
- Refresh token in HTTP-only cookie (not accessible to JS)
- On page refresh, use refresh cookie to get new access token

## Refresh Token Rotation

Every time a refresh token is used, issue a **new** refresh token and invalidate the old one.

This way, if a refresh token is stolen:
- Attacker uses it → gets new tokens
- Legitimate user uses old one → server detects reuse → revokes all tokens for that user

This is called **refresh token rotation** and is a critical security pattern.

## Production Security Checklist

### Secrets Management
- Store SECRET_KEY in environment variables, never in code
- Use `.env` in dev, but a secrets manager in production
- Rotate secrets periodically

### HTTPS
- All traffic must be HTTPS — tokens are sent with every request
- Without HTTPS, anyone on the same WiFi can steal tokens
- Use Let's Encrypt for free TLS certificates

### Rate Limiting
- Limit login attempts (e.g., 5 per minute per IP)
- Prevents brute force password guessing
- Tools: slowapi, Redis-based rate limiter

### Headers
```
Strict-Transport-Security: max-age=31536000  → Force HTTPS
X-Content-Type-Options: nosniff              → Prevent MIME sniffing
Content-Security-Policy: ...                  → Prevent XSS
```

### Logging & Audit
- Log all login attempts (success and failure)
- Log all role changes
- Log all token refreshes
- Never log passwords or token values

## Common Attack Vectors

| Attack | How it works | Defense |
|---|---|---|
| Token theft | Attacker steals token from localStorage | Short expiry, HTTP-only cookies |
| Brute force | Try many passwords | Rate limiting, slow hash |
| Timing attack | Measure response time to infer valid usernames | Dummy hash pattern |
| CSRF | Attacker makes request from their site while user is logged in | SameSite cookies, CSRF tokens |
| XSS | Attacker injects JS to read tokens | CSP headers, input sanitization |

## The Complete Auth Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│  Auth Routes  │────▶│  User DB     │
│  (React/etc) │◀────│  /login       │◀────│  (passwords) │
└──────────────┘     │  /refresh     │     └──────────────┘
       │             │  /logout      │
       │             └──────────────┘
       │                      │
       │                      ▼
       │             ┌──────────────┐
       │◀────────────│  Protected   │
       │  (token)    │  Routes      │
       │             │  /courses    │
       │             │  /users      │
       │             └──────────────┘
```

## Key Systems Insight

Auth is not a feature — it's an **infrastructure layer**. Every route depends on it. Every security decision cascades from it. Getting it right means thinking about:
1. How tokens are created
2. How tokens are verified
3. How tokens are stored (client-side)
4. How tokens are revoked
5. How the system behaves under attack
