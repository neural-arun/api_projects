# Password Hashing & Storage

## The Golden Rule

**Never store plaintext passwords. Ever.**

If your database is breached, plaintext passwords leak. Since most people reuse passwords across sites, a leak at your app means compromised accounts at banks, email, etc.

## Hashing vs Encryption

| | Hashing | Encryption |
|---|---|---|
| One-way | ✅ Cannot reverse | ❌ Can decrypt with key |
| Purpose | Verify integrity | Keep secrets |
| Used for | Passwords | Data in transit |
| Example | SHA-256, Argon2 | AES-256 |

When a user creates a password: hash it → store the hash.
When a user logs in: hash what they typed → compare with stored hash.

## What Makes a Good Password Hash

1. **Slow** — should take ~100ms to compute. Fast hashes (SHA-256, MD5) are bad.
2. **Salted** — every user gets a unique random salt. Same password → different hash.
3. **Resistant to GPU** — memory-hard algorithms (Argon2) resist hardware acceleration.

## pwdlib (FastAPI's Recommended Library)

FastAPI recommends `pwdlib` with Argon2:

```
# Recommended algorithm
PasswordHash.recommended()  → uses Argon2

# Methods
.hash(plain_password)       → returns hashed string
.verify(plain, hashed)      → returns True/False
```

The `recommended()` settings use parameters that make GPU attacks impractical.

## The Timing Attack

When checking credentials, you must avoid revealing **why** authentication failed:

```
# BAD — attacker can tell which usernames exist
if user not found:
    return False       # Fast response
if not verify(password):
    return False       # Slower response

# GOOD — same response time regardless
authenticate(username, password):
    user = find_user(username)
    if not user:
        verify(password, DUMMY_HASH)  # Waste time
        return False
    if not verify(password, user.hash):
        return False
    return user
```

This prevents attackers from enumerating valid usernames by measuring response times.

## Storage in Database

```
users table:
├── id: int (PK)
├── username: str (unique)
├── email: str (unique)
├── hashed_password: str     ← Argon2 hash, looks like:
│   "$argon2id$v=19$m=65536,t=3,p=4$..."
├── role: str                ← Student / Instructor / Admin
└── created_at: timestamp
```

You never store the original password. If the user forgets it, they reset it — you can't recover the old one.

## Key Takeaways

- Hash passwords, don't encrypt them
- Use Argon2 via pwdlib (not bcrypt, not SHA)
- Always use the dummy hash pattern for timing safety
- The hash is useless to an attacker — they can't reverse it
