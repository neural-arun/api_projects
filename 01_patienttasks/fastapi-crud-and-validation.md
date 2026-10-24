# 🩺 Build 01 · Patient Task Management API

> **Your build:** A backend where patients can add daily tasks and care-plan reminders, view them, update them, and track completion. The API stores reminder details; it does not choose treatment.

**The journey:** App → Request → FastAPI → Task action → Response

---

## ⚡ 01 · Start the API
### FastAPI · ASGI · Uvicorn

**🧠 Concept**

- **API:** The agreed way one program asks another program to do something and receives a result. The patient app calls the API instead of reaching into the server’s Python code.
- **FastAPI:** The Python framework where we define the API’s routes, input rules, and operations, such as “create a task.”
- **Uvicorn:** The web server that listens for requests from apps and passes them to the FastAPI application.
- **ASGI (Asynchronous Server Gateway Interface):** The standard handoff between Uvicorn and FastAPI. It lets the server and Python application pass requests and responses to each other.
- **Together:** Uvicorn receives; ASGI hands off; FastAPI chooses and runs the operation; the response travels back to the app.

**⚠️ Important to remember**

- Creating `app = FastAPI()` creates the application object; it does not start a web server. Uvicorn starts listening when you run the development command.
- `async def` does not automatically make code faster. Async helps when the code awaits async-friendly I/O; a blocking call inside an async route can still hold up other requests.

**🩺 In Patient Tasks**

- When a patient taps “complete,” the app sends a request to Uvicorn.
- FastAPI finds the operation for that request, updates the task, and sends the result back to the app.

**🛠 Build it**

- Add FastAPI and its standard tools. The standard extra includes Uvicorn:

  ~~~sh
  uv add "fastapi[standard]"
  ~~~

- Create the FastAPI app in `main.py`:

  ~~~python
  from fastapi import FastAPI

  app = FastAPI()
  ~~~

- Start the development server. It reloads when code changes.
- FastAPI generates `/docs` from the API’s routes and models; open it in a browser to explore and try the API.

  ~~~sh
  uv run fastapi dev main.py
  ~~~

![Mind map: Patient Tasks API](assets/mindmaps/01-api-request-flow.svg)

---

## 🌐 02 · HTTP messages  
### Requests · responses · JSON

**🧠 Concept**

- **HTTP (Hypertext Transfer Protocol):** The request-and-response conversation apps use with web servers. The app sends a request; the API sends one response.
- **Method:** Says what action the app wants, such as read (`GET`) or create (`POST`).
- **Path:** Says which resource is involved, such as `/tasks/81` for task 81.
- **Query:** Adds optional list choices, such as `?due=today`. It usually filters a result rather than naming a different operation.
- **Headers:** Carry request details, such as the data format. `Content-Type: application/json` tells the API the body is JSON.
- **Body:** Carries the data to create or change. A read request often has no body.
- **Response:** Includes a status code for the outcome and may include a body with returned data.
- **JSON (JavaScript Object Notation):** A common format for structured data. Objects use named fields; values can be text, numbers, `true`/`false`, or `null` (no value).

**⚠️ Important to remember**

- **HTTP is stateless:** Each request stands on its own. The server does not automatically remember which task the previous request was about, so include the needed ID and data each time.
- **Omitted and `null` are different:** Omitted means “no value was sent”; `null` explicitly means “there is no value.” This distinction matters when updating an optional due time.

**🩺 In Patient Tasks**

- To add a task, the app sends the title and due time in the request body.
- The API replies with the saved task, including its server-assigned ID, or an error that explains why the request was rejected.

**🛠 Build it**

- Put create/update fields in a JSON body. For example:

~~~json
{
  "title": "Walk for 20 minutes",
  "due_at": null
}
~~~

- `POST` — create a task.
- `/patients/42/tasks` — create it in patient 42’s task collection.
- The JSON body — supplies fields such as `title` and `due_at`.
- The response — reports a status and, on success, the saved task.

![Mind map: HTTP exchange](assets/mindmaps/02-http-exchange.svg)

---

## 🧭 03 · Routes & HTTP methods  
### Send each action to the right operation

**🧠 Concept**

- **Route:** A rule that connects a request to a Python operation.
- **Route match:** FastAPI checks both the HTTP method and path. `GET /tasks/81` and `PATCH /tasks/81` use the same path but run different operations.
- **Path parameter:** Identifies the resource, such as patient `42` or task `81`.
- **Query parameter:** Adds an option to a request, often to filter a list, such as `?due=today`.
- **HTTP method:** Signals the intended action. The method names are conventions that make APIs predictable for clients.

**⚠️ Important to remember**

- **Keep `GET` read-only.** Browsers, caches, or clients may repeat a `GET`; it should not mark a task complete or otherwise change data.
- **Specific routes can overlap with variable routes.** If you add `/tasks/today` as well as `/tasks/{task_id}`, declare the fixed `/tasks/today` route first so `today` is not treated as an ID.
- **An ID is not permission.** Knowing `/tasks/81` must not be enough to read or change it; a later authenticated version must also check that the signed-in user may access that task.

**🩺 In Patient Tasks**

- Use a patient ID in the path to find that patient’s tasks and a task ID to target one task.
- Use a query value to filter the list without changing which operation runs.

**🛠 Build it**

- `GET /patients/42/tasks` — read patient 42’s task list. Add `?due=today` to filter it.
- `GET /tasks/81` — read one task.
- `POST /patients/42/tasks` — create a task for patient 42.
- `PUT /tasks/81` — replace the task by sending its full new representation.
- `PATCH /tasks/81` — change only selected fields, such as its completion status.
- `DELETE /tasks/81` — remove the task.
- For this beginner project, remember: `PUT` sends a replacement; `PATCH` sends only changes.

![Mind map: Routes](assets/mindmaps/03-routes-and-methods.svg)

---

## 📦 04 · Pydantic BaseModel  
### Describe the data shape

**🧠 Concept**

- **Model/schema:** A description of the data an API accepts or returns: field names, types, and required values. Think of it as a form definition.
- **Pydantic `BaseModel`:** The Python tool used to define that description.
- **Parsing:** FastAPI reads the JSON body and Pydantic turns it into a Python object whose fields can be accessed by name.
- **Type checking:** Pydantic checks values against the declared types. If required fields are missing or values cannot be accepted, FastAPI returns a validation error before the operation changes a task.
- **Important boundary:** These models define the API’s data shape. They do not save data in a database by themselves.

**⚠️ Important to remember**

- In Pydantic v2, `due_at: datetime | None` allows `null`, but the field is still required unless it has a default such as `= None`.
- For partial updates, save only fields the client actually sent. In Pydantic, `model_dump(exclude_unset=True)` helps keep omitted fields from accidentally overwriting saved values.

**🩺 In Patient Tasks**

- **Create model:** Requires a title; the due time can be absent. The server supplies the ID and initial `completed = false` value.
- **Update model:** Accepts only the fields the patient wants to change.
- **Response model:** Includes the saved task’s ID, title, due time, and completion state.

**🛠 Build it**

- Use separate models for task creation, partial updates, and responses; each has a different job.
- A field with a default can be omitted from the request.
- A field that allows `null` can explicitly have no value; for example, a patient could clear a task’s due time.
- For a partial update, an omitted field means “keep the current value”; a supplied value means “change it.”
- This difference matters: if the patient omits `due_at`, keep its old value; if they send `"due_at": null`, clear it.


![Mind map: Task data](assets/mindmaps/04-task-data.svg)

---

## ✅ 05 · Validation  
### Catch invalid data before saving

**🧠 Concept**

- **Purpose:** Check a request before using its data, so invalid input does not corrupt or confuse task data.
- **Shape/type checks:** Is `title` text? Is `completed` a true/false value? Are required fields present? FastAPI and Pydantic handle many of these checks.
- **Field rules:** Does the title contain something besides spaces? Is the due time in a format we understand? We add rules like these to the application.
- **Business rules:** Is this action allowed for this task? For example, a completed task may not be editable in a future version of the project.
- **Validation vs permission:** Valid data does not prove the user is allowed to change a task. The API must check permission separately when the project adds users and authentication.

**⚠️ Important to remember**

- FastAPI checks the request shape before it runs the route function. If the body is invalid, the code that changes the task does not run.
- Validation answers “is this data acceptable?” Authorization answers “is this user allowed?” A request can pass validation and still be forbidden.

**🩺 In Patient Tasks**

- Reject a blank title, a date/time the API cannot understand, or a completion value that is not true or false.
- A request can have the right shape and still break a project rule. Check both before changing a task.
- Reminder details must come from an authorized care plan; valid input alone does not grant permission to create a reminder.

**🛠 Build it**

- Let FastAPI/Pydantic report missing or wrongly typed fields.
- Add task-specific checks before changing the task.
- Return status `422` for invalid request data. It tells the app to correct the request and try again.

![Mind map: Validation](assets/mindmaps/05-validation.svg)

---

## 🔁 06 · CRUD  
### Manage task records

**🧠 Concept**

- **Create:** Add a new record.
- **Read:** Fetch one record or a list of records.
- **Update:** Change some or all fields on an existing record.
- **Delete:** Remove a record or make it no longer available.
- CRUD describes what happens to the data; HTTP methods and routes are how a client asks the API to do it.

**⚠️ Important to remember**

- A Python list is temporary storage, not a database. Restarting the app clears it.
- Each Uvicorn worker is a separate process with its own memory. With multiple workers, one may not see a task another worker added; use a shared database for real persistence.

**🩺 In Patient Tasks**

- Create a task, read one task or the patient’s list, update its title or completion state, and delete it.
- Each action must target the intended task and tell the app what happened.

**🛠 Build it**

- Connect each CRUD action to a route.
- Use an in-memory list for this first exercise. It is simple, but it disappears when the server restarts and is not shared between separate server processes.
- Build 2 adds a database so tasks remain saved after the API stops.

![Mind map: CRUD tasks](assets/mindmaps/06-crud.svg)

---

## 📤 07 · Response models & status codes  
### Return a predictable result

**🧠 Concept**

- **Response model:** Describes the fields and types the API sends back. It makes the output predictable and can keep internal fields out of the response.
- **Status code:** A standard number that summarizes the result. The app can react to it without guessing from a message.
- **2xx:** The request succeeded.
- **4xx:** The request could not be completed as sent, for example because the task was missing or the data was invalid.

**⚠️ Important to remember**

- A response model only protects fields that are left out of that model. If a field is added to the response schema, the API may expose it to clients.
- `204` means there is no response body. If the app needs the deleted task returned, choose a response that includes a body instead.

**🩺 In Patient Tasks**

- Return the task ID, title, due time, and completion status in the same shape after creating, reading, or updating a task.
- The app can display those known fields without depending on internal server details.

**🛠 Build it**

- Use a task response model for create/read/update results.
- `200` — read or update succeeded; the response usually includes the task.
- `201` — the task was created; the response can include the new task.
- `204` — the task was deleted; there is no response body.
- `404` — the requested task was not found.
- `422` — the request data failed validation.

![Mind map: API response](assets/mindmaps/07-responses.svg)

---

## 🚨 08 · HTTPException  
### Report expected errors

**🧠 Concept**

- **Expected error:** A normal situation the API should handle, such as asking for a task that does not exist.
- **Raise `HTTPException`:** Stop the current operation immediately and return the chosen HTTP status and `detail` message to the app.
- **Safe detail:** Explain the problem in a way the user can act on, without exposing internal code or sensitive data.
- **Not every failure is expected:** A missing task is a 404; invalid input is usually a 422; an unexpected bug should become a generic 500 response while its technical details stay in server logs.

**⚠️ Important to remember**

- Use `raise HTTPException(...)`, not `return HTTPException(...)`. Raising stops the route and lets FastAPI build the error response.
- The `detail` text is sent to the client. Keep it useful and safe; do not put stack traces, database errors, or private patient information there.

**🩺 In Patient Tasks**

- If task 81 does not exist, return `404` so the app knows there is nothing to update.
- Returning success would mislead the app and the patient into thinking the task changed.

**🛠 Build it**

- Look up the task before updating or deleting it.
- If it is missing, raise `HTTPException` with status `404` and a short, safe message. The route stops instead of trying to change a nonexistent task.
- Let FastAPI return `422` for invalid request data. Keep unexpected technical details in server logs, not in the response.

![Mind map: HTTPException](assets/mindmaps/08-errors.svg)

---

## 🧩 One request, end to end

**Example:** The patient marks task 81 complete by sending:

~~~http
PATCH /tasks/81
Content-Type: application/json

{"completed": true}
~~~

**Follow the request:**

- **Receive:** Uvicorn receives the HTTP request and hands it to FastAPI through ASGI.
- **Choose the operation:** FastAPI matches `PATCH /tasks/{task_id}` and reads `81` as the task ID.
- **Check the body:** Pydantic turns the JSON into update data; validation checks `completed` is true or false.
- **Apply the change:** The task operation finds task 81 and changes its completion state.
- **Reply:** The response model shapes the returned task; status `200` tells the app the update succeeded.
- **If the task is missing:** The operation stops and returns `404` instead.

~~~mermaid
---
config:
  theme: neutral
  look: classic
---
flowchart LR
  A[Patient app] --> B[Uvicorn]
  B -->|ASGI| C[FastAPI route]
  C --> D[JSON and Pydantic]
  D --> E[Validation]
  E -->|valid| F[CRUD update]
  F --> G[Response model and status]
  G --> H[Patient app]
  E -->|invalid| I[422 error]
  C -->|task missing| J[HTTPException 404]
~~~

### 📚 Official references

- **FastAPI:** [first steps](https://fastapi.tiangolo.com/tutorial/first-steps/) · [request bodies](https://fastapi.tiangolo.com/tutorial/body/) · [path and query parameters](https://fastapi.tiangolo.com/tutorial/query-params/) · [response models](https://fastapi.tiangolo.com/tutorial/response-model/) · [errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- **Runtime:** [ASGI specification](https://asgi.readthedocs.io/en/latest/specs/main.html) · [Uvicorn](https://www.uvicorn.org/)
