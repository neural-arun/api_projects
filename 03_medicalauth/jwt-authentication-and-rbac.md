# 🔐 Build 03 · Medical Education Auth Platform

> **Your build:** Students, instructors, and admins can register and sign in. The API checks who they are and what each role is allowed to do.

**The journey:** Register → verify password → sign in → receive token → access allowed routes

---

## 🪪 01 · Authentication vs authorization

**🧠 Concept**

- **Authentication:** Proves who the user is, usually by checking a password or another sign-in factor.
- **Authorization:** Decides what an authenticated user may do, based on a role, permission, ownership, or other policy.
- **Role:** A named group of permissions, such as `student`, `instructor`, or `admin`.
- A user may be signed in but still lack permission to use a particular operation.

**⚠️ Important to remember**

- Hiding a button in the browser is not security. A user can call the API directly, so enforce permissions on the server for every protected operation.
- A role alone may not be enough: also check which course or account the user may access. Use `401` for not signed in and `403` for signed in but not allowed.

**🩺 In this platform**

- A student can view learning material; an instructor can manage lessons; an admin can manage users and roles.
- The API checks the user's identity and permission before returning or changing protected data.

**🛠 Build it**

- Define student, instructor, and admin roles and list the actions each role may perform.
- For each protected operation, check the signed-in user’s role and any needed resource ownership on the server.
- Deny access by default when no rule explicitly allows the action.

![Mind map: Access decision](assets/mindmaps/01-auth-vs-authorization.svg)

---

## 🎟️ 02 · OAuth2 & JWT  
### Sign in and carry access

**🧠 Concept**

- **OAuth 2.0:** A standard framework for granting limited access to an API. A bearer token is sent with a request to prove the caller has a valid access token.
- **JWT:** A compact token containing claims, such as a user ID (`sub`) and expiry (`exp`). It is commonly used to carry identity-related information between requests.
- A signed JWT has a header, payload, and signature. The API checks the signature and expiry before trusting its claims.
- A signature detects changes; it does not hide the payload. Anyone holding a normal signed JWT can usually read its contents.

**⚠️ Important to remember**

- Do not put passwords, signing keys, or sensitive student data in a JWT. Signing is not encryption.
- JWTs are difficult to revoke before they expire unless the system tracks revocation. Keep access tokens short-lived and protect, rotate, and revoke refresh tokens.

**🩺 In this platform**

- After sign-in, the client sends its access token with later requests.
- FastAPI verifies the token and uses its trusted user ID to make an authorization decision.

**🛠 Build it**

- Registration stores a password hash; login verifies the submitted password before issuing a token.
- Use a bearer-token flow for protected requests. OpenID Connect adds standard identity information on top of OAuth2 when needed.
- Keep access tokens short-lived. Use a refresh token to obtain a new access token; protect, rotate, and revoke refresh tokens.
- Put only necessary claims in a JWT and verify its signature and expiry on every request.

![Mind map: Sign-in and access tokens](assets/mindmaps/02-oauth2-jwt.svg)

---

## 🧂 03 · Password hashing  
### Never save a readable password

**🧠 Concept**

- **Hashing:** Turns a password into a one-way value that can be checked later; it is designed not to be reversed.
- **Encryption:** Protects data in a reversible form when the right key is available. Passwords should be hashed, not encrypted for later recovery.
- **Salt:** A unique random value mixed into a password before hashing. It makes equal passwords produce different stored hashes and defeats precomputed lookup tables.
- A password-hashing algorithm is deliberately slow, making large-scale guessing more expensive.

**⚠️ Important to remember**

- Do not use a fast general-purpose hash such as SHA-256 for passwords. Use a maintained password-hashing library with its recommended algorithm and settings.
- Let the library generate and store the salt as part of the encoded hash. Never store or log the original password.

**🩺 In this platform**

- Registration stores the password hash, not the password.
- Login checks the submitted password against the stored hash; only a match allows sign-in and token issuance.

**🛠 Build it**

- Use a maintained password-hashing library and its recommended settings.
- The syllabus names bcrypt; before a new production system, check current security guidance and the library’s recommendations.
- Never store or log plain passwords.

![Mind map: Password safety](assets/mindmaps/03-password-hashing.svg)

---

## 🧱 04 · RBAC, middleware & secrets  
### Apply security consistently

**🧠 Concept**

- **RBAC:** Role-Based Access Control assigns permissions to roles, then assigns users to those roles.
- **Dependency or middleware:** Shared request-handling code. A FastAPI dependency is useful for checks on chosen routes; middleware runs around many or all requests and suits cross-cutting tasks such as request IDs.
- **Secret:** A credential such as a signing key or database password. Anyone who gets it may be able to impersonate the service or access its data.

**⚠️ Important to remember**

- Middleware is not automatically the right place for every permission check. Route-specific authorization is often clearer as a dependency that names the requirement.
- A secret committed to Git should be considered exposed. Remove it from use and rotate it; deleting the visible line does not erase it from Git history.

**🩺 In this platform**

- A course-management route can require instructor or admin permission, while a learning-material route can allow students.
- The check must happen in the API even if the interface already hides actions from that role.

**🛠 Build it**

- Write a role/action table before adding protected routes.
- Put reusable sign-in and role checks into dependencies; use middleware for genuinely shared request behavior.
- Load signing keys and database credentials from environment configuration.
- Keep local secrets out of Git; rotate any exposed keys.

![Mind map: Protect every request](assets/mindmaps/04-rbac-secrets.svg)

### 📚 Official references

- [FastAPI OAuth2, JWT, and password hashing](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [OAuth 2.0 specification](https://datatracker.ietf.org/doc/html/rfc6749) · [JWT specification](https://datatracker.ietf.org/doc/html/rfc7519)
- [OWASP password storage guidance](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
