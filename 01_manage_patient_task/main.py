# Step 1: Import FastAPI
from fastapi import FastAPI, status, HTTPException
# Step 3: We need Pydantic to define the request body shape
from pydantic import BaseModel

# Create the FastAPI app instance
# This is what uvicorn runs when we say "uvicorn main:app"
app = FastAPI()

# Step 2: In-memory storage
# A simple list to hold all our tasks (no database yet)
tasks: list[dict] = []
# Counter to assign unique IDs to each new task
next_id: int = 1

# Step 3: Pydantic model for creating a task
# This defines what the client must send in the POST request body
class TaskCreate(BaseModel):
    title: str                     # Required — task name
    description: str | None = None # Optional — extra details
    patient_name: str              # Required — who this task is for

# Step 6: Pydantic model for updating a task
# All fields are optional — client only sends what they want to change
class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    patient_name: str | None = None

# POST /tasks — Create a new task
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    global next_id  # We need to modify the counter

    # Build the task dictionary with all fields
    new_task = {
        "id": next_id,
        "title": task.title,
        "description": task.description,
        "patient_name": task.patient_name,
        "is_completed": False,  # New tasks start as not done
    }

    # Store it and increment the ID counter
    tasks.append(new_task)
    next_id += 1

    # Return the created task (FastAPI converts this dict to JSON)
    return new_task

# Step 4: GET /tasks — List all tasks
# The `status` query param is optional — if not provided, returns all tasks
# Example: GET /tasks       → returns all tasks
# Example: GET /tasks?status=completed → returns only completed tasks
# Example: GET /tasks?status=pending   → returns only pending tasks
@app.get("/tasks")
def list_tasks(status: str | None = None):
    # If no status filter, return everything
    if status is None:
        return tasks

    # Filter based on status value
    if status == "completed":
        # Return only tasks where is_completed is True
        return [t for t in tasks if t["is_completed"]]
    elif status == "pending":
        # Return only tasks where is_completed is False
        return [t for t in tasks if not t["is_completed"]]

    # Invalid status value — return empty list
    return []

# Step 5: GET /tasks/{task_id} — Get a single task by its ID
# The {task_id} is a path parameter — it's part of the URL itself
# FastAPI converts it to int automatically because of the type hint
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    # Loop through tasks to find the one with matching ID
    for task in tasks:
        if task["id"] == task_id:
            return task

    # If no task found with that ID, raise 404
    raise HTTPException(status_code=404, detail="Task not found")

# Step 6: PUT /tasks/{task_id} — Update a task
# Client sends only the fields they want to change (all optional)
# Fields that are None are skipped — existing value is kept
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate):
    # Find the task first
    for task in tasks:
        if task["id"] == task_id:
            # Only update fields that were actually sent (not None)
            if task_update.title is not None:
                task["title"] = task_update.title
            if task_update.description is not None:
                task["description"] = task_update.description
            if task_update.patient_name is not None:
                task["patient_name"] = task_update.patient_name

            return task

    # If task_id doesn't exist
    raise HTTPException(status_code=404, detail="Task not found")

# Step 7: PATCH /tasks/{task_id}/complete — Mark task as done
# No request body needed — this endpoint just flips is_completed to True
# PATCH is used because we're only changing one field (partial update)
@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    # Find the task
    for task in tasks:
        if task["id"] == task_id:
            # Flip the completion status to True
            task["is_completed"] = True
            return task

    # If task_id doesn't exist
    raise HTTPException(status_code=404, detail="Task not found")

# Step 8: DELETE /tasks/{task_id} — Delete a task
# Status 204 means "No Content" — we send back an empty body
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    # Loop through tasks with index so we can remove by position
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            # Remove the task from the list
            tasks.pop(index)
            # Return None so FastAPI sends an empty 204 response
            return None

    # If task_id doesn't exist
    raise HTTPException(status_code=404, detail="Task not found")
