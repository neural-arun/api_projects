# Quiz — Build 7: Medical Document Processing Pipeline

### Q1
You upload a PDF. The route calls `process_pdf.delay(file_id)`. When does `process_pdf` actually run?

- A) Immediately, in the same request
- B) After the response is sent, in the same process
- C) Whenever a Celery worker picks it up from the queue
- D) At midnight

**Answer:** C

### Q2
**True or False:** If a Celery worker crashes while processing a task, the task is lost forever.

**Answer:** False — with `task_acks_late = True`, unacknowledged tasks go back to the queue.

### Q3
What does `.delay()` do that's different from calling the function directly?

- A) It delays execution by 5 seconds
- B) It serializes arguments, sends them to Redis, and returns a task ID
- C) It runs the function in a thread pool
- D) It deletes the function after running

**Answer:** B

### Q4
Why can't you use FastAPI's BackgroundTasks for processing large medical PDFs?

- A) BackgroundTasks can only send emails
- B) BackgroundTasks run in the same process — if the server restarts, tasks are lost
- C) BackgroundTasks are slower than Celery
- D) BackgroundTasks can't access the database

**Answer:** B

### Q5
**Scenario:** A patient detail endpoint is getting 1000 requests/second. Each request hits the database. What's the fix?

- A) Add more database replicas
- B) Cache patient data in Redis with a TTL
- C) Rate-limit the endpoint
- D) Combine all patients into one response

**Answer:** B

### Q6
**True or False:** If you update a patient's name in the database, the cached version in Redis updates automatically.

**Answer:** False — you must explicitly invalidate or update the cache when data changes.

### Q7
What's the difference between Redis as a broker vs Redis as a result backend?

- A) Nothing — they're the same
- B) Broker stores pending tasks; result backend stores task outputs
- C) Broker stores completed tasks; result backend stores pending tasks
- D) Broker is for Celery; result backend is for caching

**Answer:** B

### Q8
A task fails with "File not found" every time it retries. What should you do?

- A) Increase max_retries to 10
- B) Don't retry — this is a permanent failure, not transient
- C) Increase retry_delay
- D) Restart the worker

**Answer:** B

### Q9
**Scenario:** You deploy 10 API servers and 3 Celery workers. Where does the bottleneck likely appear?

- A) API servers — too many
- B) Celery workers — too few for the task volume
- C) Redis — can't handle the load
- D) PostgreSQL — too many connections

**Answer:** B — API servers can queue tasks faster than 3 workers can process them.

### Q10
What status code should a route return when it queues a task instead of completing it?

- A) 200 OK
- B) 201 Created
- C) 202 Accepted
- D) 204 No Content

**Answer:** C — 202 Accepted means "we got your request and will process it later."
