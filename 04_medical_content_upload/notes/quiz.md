# Quiz — Medical Content Upload API

**Instructions:** Choose the correct answer for each question.

---

## Q1. What content type does HTTP use for file uploads?
- [ ] A) `application/json`
- [ ] B) `application/x-www-form-urlencoded`
- [ ] C) `multipart/form-data`
- [ ] D) `text/plain`
C

---

## Q2. Why must you install `python-multipart`?
- [ ] A) It's required to run FastAPI at all
- [ ] B) FastAPI doesn't parse multipart/form-data without it
- [ ] C) It enables async file reading
- [ ] D) It provides file validation utilities
B

---

## Q3. Which should you use for a 200 MB medical scan upload?
- [ ] A) `file: bytes = File()`
- [ ] B) `file: UploadFile = File()`
- [ ] C) `file: str = File()`
- [ ] D) `file: dict = File()`
B

---

## Q4. What does `UploadFile.content_type` contain?
- [ ] A) The detected MIME type from magic bytes
- [ ] B) The MIME type sent by the client
- [ ] C) The file extension
- [ ] D) Always `application/octet-stream`
B

---

## Q5. Why should you check magic bytes instead of trusting `content_type`?
- [ ] A) Magic bytes are faster
- [ ] B) The client can lie about the content type
- [ ] C) `content_type` is always None
- [ ] D) Magic bytes are required by law
B

---

## Q6. What is the best way to store uploaded medical files on disk?
- [ ] A) In the `static/` folder with original filenames
- [ ] B) Outside the web root with UUID filenames
- [ ] C) In a database BLOB column
- [ ] D) In `/tmp/` with original filenames
B

---

## Q7. What does `UploadFile.seek(0)` do?
- [ ] A) Deletes the file
- [ ] B) Resets the read pointer to the beginning
- [ ] C) Validates the file
- [ ] D) Closes the file
B

---

## Q8. In FastAPI, `def` route handlers run in:
- [ ] A) The main event loop
- [ ] B) A thread pool
- [ ] C) A separate process
- [ ] D) The browser
B

---

## Q9. Which operation is CPU-bound (should use `def`, not `async def`)?
- [ ] A) Reading a file from disk
- [ ] B) Sending an HTTP request
- [ ] C) Parsing a PDF with PyPDF2
- [ ] D) Querying a database
C

---

## Q10. What does `BackgroundTasks.add_task()` do?
- [ ] A) Runs a function in a separate process
- [ ] B) Schedules a function to run after the response is sent
- [ ] C) Runs a function before the request handler
- [ ] D) Creates a new thread for each request
B

---

## Q11. Which is a valid limitation of `BackgroundTasks`?
- [ ] A) Functions must be async
- [ ] B) Tasks can only take keyword arguments
- [ ] C) Tasks run in the same process — heavy work slows the server
- [ ] D) Only one task can be scheduled per request
C

---

## Q12. What does `StreamingResponse` do differently from `FileResponse`?
- [ ] A) It sends the entire file at once
- [ ] B) It takes an iterable and sends data in chunks
- [ ] C) It only works with text files
- [ ] D) It requires a database connection
B

---

## Q13. What HTTP status code does a server return for a partial content (range) request?
- [ ] A) 200
- [ ] B) 201
- [ ] C) 206
- [ ] D) 304
C

---

## Q14. What is the correct order of the upload pipeline?
- [ ] A) Store → Validate → Record → Respond → Background
- [ ] B) Validate → Store → Record → Respond → Background
- [ ] C) Record → Validate → Store → Respond → Background
- [ ] D) Background → Validate → Store → Record → Respond
B

## Answer Key

| Q | Answer |
|---|---|
| 1 | C |
| 2 | B |
| 3 | B |
| 4 | B |
| 5 | B |
| 6 | B |
| 7 | B |
| 8 | B |
| 9 | C |
| 10 | B |
| 11 | C |
| 12 | B |
| 13 | C |
| 14 | B |
