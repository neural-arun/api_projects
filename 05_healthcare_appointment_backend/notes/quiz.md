# Build 5 Quiz — Healthcare Appointment Backend

**Instructions:** Tick your answer by changing `[ ]` to `[x]`.

---

## Q1. What is the purpose of a service layer in FastAPI?

- [ ] A) To handle HTTP request parsing
- [ ] B) To contain business logic separate from routes
- [ ] C) To define database table schemas
- [ ] D) To configure environment variables

---

## Q2. In the service layer pattern, which layer is responsible for returning the correct HTTP status code?

- [ ] A) Service layer
- [ ] B) Model layer
- [ ] C) Router layer
- [ ] D) Database layer

---

## Q3. What does pydantic-settings `BaseSettings` provide over plain `os.getenv()`?

- [ ] A) Type coercion and validation
- [ ] B) Automatic database migration
- [ ] C) API route generation
- [ ] D) Logging configuration

---

## Q4. What does the ACID property "Atomicity" guarantee?

- [ ] A) Data is consistent across tables
- [ ] B) A transaction completes entirely or not at all
- [ ] C) Concurrent transactions don't interfere
- [ ] D) Committed data survives crashes

---

## Q5. In SQLAlchemy, what happens when you call `session.commit()`?

- [ ] A) The session is closed
- [ ] B) All staged changes are written to the database
- [ ] C) Changes are discarded
- [ ] D) A new transaction begins

---

## Q6. What does `session.rollback()` do?

- [ ] A) Closes the database connection
- [ ] B) Undoes all changes since the last commit
- [ ] C) Commits the current transaction
- [ ] D) Creates a savepoint

---

## Q7. Which log level should you use for normal operational events like "Appointment created"?

- [ ] A) DEBUG
- [ ] B) INFO
- [ ] C) WARNING
- [ ] D) ERROR

---

## Q8. Why should you NOT log patient names or medical conditions?

- [ ] A) They take too much disk space
- [ ] B) Healthcare privacy regulations (HIPAA/GDPR) prohibit it
- [ ] C) It slows down the application
- [ ] D) Python logging can't handle strings with spaces

---

## Q9. In pytest, what is a fixture used for?

- [ ] A) Defining test functions
- [ ] B) Setting up and tearing down test resources
- [ ] C) Asserting test conditions
- [ ] D) Running tests in parallel

---

## Q10. What does FastAPI's `TestClient` require to be installed?

- [ ] A) requests
- [ ] B) httpx
- [ ] C) urllib3
- [ ] D) aiohttp

---

## Q11. How do you inject an `AppointmentService` into a route?

- [ ] A) Import it directly and instantiate it
- [ ] B) Use `Depends()` with a factory function
- [ ] C) Add it to the route decorator
- [ ] D) Use a global variable

---

## Q12. What SQL query does `check_conflict()` use to detect double booking?

- [ ] A) Exact match on start_time
- [ ] B) Overlapping time ranges: `start < existing_end AND end > existing_start`
- [ ] C) Match on doctor_id only
- [ ] D) Match on patient_id only

---

## Q13. What should you include in `.gitignore` for this project?

- [ ] A) `app/` directory
- [ ] B) `.env` file
- [ ] C) `tests/` directory
- [ ] D) `requirements.txt`

---

## Q14. What does `app.dependency_overrides` allow you to do in tests?

- [ ] A) Skip tests
- [ ] B) Replace a dependency (like get_session) with a test version
- [ ] C) Speed up tests
- [ ] D) Log test output

---

## Q15. Which HTTP status code should you return when a double booking is detected?

- [ ] A) 200 OK
- [ ] B) 201 Created
- [ ] C) 404 Not Found
- [ ] D) 409 Conflict

---

## Answer Key

| Q | Answer | Explanation |
|---|---|---|
| 1 | B | Service layer contains business logic; routers handle HTTP |
| 2 | C | Router layer returns status codes based on service results |
| 3 | A | BaseSettings provides type coercion and validation at import |
| 4 | B | Atomicity = all-or-nothing execution |
| 5 | B | commit() writes all staged changes permanently |
| 6 | B | rollback() undoes uncommitted changes |
| 7 | B | INFO for normal operations, DEBUG for details |
| 8 | B | Healthcare regulations prevent logging PII |
| 9 | B | Fixtures set up resources (DB, client) for tests |
| 10 | B | TestClient is built on httpx |
| 11 | B | Define a factory function and pass it to Depends() |
| 12 | B | Conflict = overlapping time ranges |
| 13 | B | .env contains secrets, never commit it |
| 14 | B | Override real deps with test doubles during testing |
| 15 | D | 409 Conflict indicates resource conflict |
