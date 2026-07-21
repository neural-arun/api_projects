# Build 3 — Medical Education Auth Platform — Notes Index

Read these in order. Each builds on the previous one.

| # | Note | What You'll Learn |
|---|---|---|
| 01 | Why Authentication Matters | Auth vs Authz, stateless HTTP, threat model |
| 02 | Password Hashing & Storage | How passwords are stored safely, pwdlib |
| 03 | OAuth2 & Bearer Tokens | The flow, token exchange, fastapi.security |
| 04 | JWT Deep Dive | Stateless tokens, signature, expiry, claims |
| 05 | Role-Based Access Control | Students, Instructors, Admin — who can do what |
| 06 | Middleware & CORS | Request pipeline, cross-origin, frontend integration |
| 07 | Refresh Tokens & Production | Token rotation, security best practices |

## The System Mindset

Don't memorize JWT syntax. Understand:
- What happens when a user logs in — the entire token lifecycle
- How the server knows who made the request on every subsequent call
- Where vulnerabilities live (token theft, password leaks, timing attacks)
- How roles cascade through the system to protect resources

## Official References

- https://fastapi.tiangolo.com/tutorial/security/
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/
- https://fastapi.tiangolo.com/tutorial/middleware/
