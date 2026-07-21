# Quiz — Build 3: Medical Education Auth Platform

**Instructions:** Answer each question. Focus on understanding the **system**, not memorizing syntax.

---

### Q1
A user logs in. The server sends back a JWT. The client stores it in localStorage.

**True or False:** The JWT payload (user id, role, expiry) is encrypted and cannot be read by the client.

**Answer:** ________

---

### Q2
Which of these describes the difference between Authentication and Authorization?

- A) Authentication is checking the password; Authorization is checking the role
- B) Authentication happens once; Authorization happens on every request
- C) Authentication identifies the user; Authorization determines what they can do
- D) Both A and C

**Answer:** ________

---

### Q3
**True or False:** An attacker who steals your SECRET_KEY can forge valid JWT tokens for any user.

**Answer:** ________

---

### Q4
Why should password hashing be **slow** (100ms+)?

- A) To annoy users
- B) To make brute force attacks impractical
- C) To reduce server load
- D) Because FastAPI requires it

**Answer:** ________

---

### Q5
A developer stores passwords using SHA-256 (fast hash). What's the biggest risk?

- A) SHA-256 is broken and can be reversed
- B) An attacker with the hash database can try billions of passwords per second
- C) SHA-256 doesn't produce consistent output
- D) SHA-256 is too slow

**Answer:** ________

---

### Q6
**Scenario:** A student copies their JWT token, modifies the `role` from "student" to "admin" in the payload, and sends it back. What happens?

- A) The server trusts the new role — they become admin
- B) The server rejects the token — signature verification fails
- C) The server checks the database and overrides the role
- D) The server crashes

**Answer:** ________

---

### Q7
What is the primary purpose of a short access token expiry (15 min)?

- A) Reduce server load
- B) Limit damage if a token is stolen
- C) Force users to re-authenticate often
- D) Comply with regulations

**Answer:** ________

---

### Q8
**True or False:** Using `allow_origins=["*"]` in CORSMiddleware prevents you from using credentialed requests (Authorization headers, cookies).

**Answer:** ________

---

### Q9
You have three endpoints. Which approach correctly enforces that only Instructors can create courses?

- A) Check `user.role == "instructor"` inside the route function
- B) Create a `require_role("instructor")` dependency and apply it to the route
- C) Create a middleware that blocks all non-instructor requests
- D) Add a boolean field `is_instructor` to the JWT token

**Answer:** ________

---

### Q10
**Scenario:** A user reports they keep getting logged out every 15 minutes. What's likely happening?

- A) Their account is being hacked
- B) The access token is expiring and there's no refresh token mechanism
- C) The server is restarting
- D) The SECRET_KEY is being rotated

**Answer:** ________

---

### Q11
**True or False:** If your database of password hashes is stolen, the attacker can immediately log in as any user.

**Answer:** ________

---

### Q12
A middleware adds a custom header to every response. A dependency checks the user's role. Which runs first?

- A) Middleware always runs before dependencies
- B) Dependencies run before middleware
- C) It depends on the order they're defined
- D) They run in parallel

**Answer:** ________

---

### Q13
What does `OAuth2PasswordBearer(tokenUrl="/token")` do for the /docs UI?

- A) It hides the endpoint from docs
- B) It adds an "Authorize" button that lets users input credentials
- C) It automatically creates the /token endpoint
- D) It disables authentication in docs

**Answer:** ________

---

### Q14
**Scenario:** A student leaves the institution. You need to immediately prevent them from accessing the API. Their access token has 20 minutes left.

- A) Change the SECRET_KEY — all tokens are invalidated
- B) Wait 20 minutes for the token to expire
- C) Add the student's token to a blocklist (e.g., Redis) and check it on every request
- D) Delete the student's account from the database

**Answer:** ________

---

### Q15
What's the difference between 401 Unauthorized and 403 Forbidden?

- A) There's no difference — they're interchangeable
- B) 401 means "not authenticated" (no token), 403 means "not authorized" (wrong role)
- C) 401 means "wrong password", 403 means "account disabled"
- D) 401 is for web requests, 403 is for API requests

**Answer:** ________

---

## Answer Key

| Q | Answer | Why |
|---|---|---|
| 1 | False | JWT payload is base64-encoded, not encrypted. Anyone can decode and read it. |
| 2 | D | Both A and C are correct. Authn = who you are. Authz = what you can do. |
| 3 | True | The SECRET_KEY signs tokens. With it, you can create valid tokens for any user ID and any role. |
| 4 | B | Slow hashing (~100ms) means an attacker can only try ~10 passwords/second instead of billions. |
| 5 | B | SHA-256 is designed to be fast. An attacker with GPUs can try billions of passwords per second against the stolen hash list. |
| 6 | B | The signature won't match after modifying the payload. The server detects tampering and rejects the token. |
| 7 | B | Short expiry = limited window of vulnerability if a token is stolen. |
| 8 | True | The CORS spec forbids wildcard origins with credentialed requests. You must list specific origins. |
| 9 | B | A reusable dependency is the cleanest approach — it can be tested, reused, and composed. |
| 10 | B | They have an access token with no refresh token mechanism. The token expires and they have no way to get a new one. |
| 11 | False | Hashes can't be reversed. The attacker would need to guess each password (one at a time, slowly). |
| 12 | A | Middleware wraps the entire app — it runs before any route or dependency processing. |
| 13 | B | It tells the /docs (Swagger UI) to show an Authorize button that sends `Authorization: Bearer <token>` on all requests. |
| 14 | C | A blocklist (in Redis) is the only way to revoke a JWT before expiry without logging out all users. |
| 15 | B | 401 = missing/invalid authentication. 403 = authenticated but not allowed. This is a universal HTTP convention. |
