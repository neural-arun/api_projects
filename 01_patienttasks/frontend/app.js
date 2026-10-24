const patientForm = document.querySelector("#patient-form");
const patientInput = document.querySelector("#patient-id");
const activePatientLabel = document.querySelector("#active-patient-label");
const taskForm = document.querySelector("#task-form");
const titleInput = document.querySelector("#task-title");
const dueInput = document.querySelector("#task-due-at");
const taskList = document.querySelector("#task-list");
const taskCount = document.querySelector("#task-count");
const emptyState = document.querySelector("#empty-state");
const emptyTitle = document.querySelector("#empty-title");
const emptyCopy = document.querySelector("#empty-copy");
const notice = document.querySelector("#notice");
const filters = document.querySelector("#task-filters");
const detailsDialog = document.querySelector("#details-dialog");
const editDialog = document.querySelector("#edit-dialog");
const editForm = document.querySelector("#edit-form");
const editTaskId = document.querySelector("#edit-task-id");
const editTaskName = document.querySelector("#edit-task-name");
const editTaskDue = document.querySelector("#edit-task-due");
const editTaskCompleted = document.querySelector("#edit-task-completed");

let activePatientId = 42;
let activeFilter = "all";
let tasks = [];
let isLoading = true;
let loadFailed = false;

function tasksUrl() {
  const baseUrl = `/patients/${activePatientId}/tasks`;
  if (activeFilter === "todo") return `${baseUrl}?completed=false`;
  if (activeFilter === "done") return `${baseUrl}?completed=true`;
  return baseUrl;
}

async function apiRequest(path, options = {}) {
  const headers = new Headers(options.headers ?? {});
  if (options.body) headers.set("Content-Type", "application/json");

  let response;
  try {
    response = await fetch(path, { ...options, headers });
  } catch {
    throw new Error("Could not connect to the API. Is the FastAPI server running?");
  }

  // DELETE returns 204 with an empty body, so there is no JSON to read.
  if (response.status === 204) return null;

  let body = null;
  try {
    body = await response.json();
  } catch {
    // Some responses do not include a JSON body.
  }

  if (!response.ok) {
    const detail = body?.detail;
    throw new Error(
      typeof detail === "string" ? detail : "The request could not be completed.",
    );
  }

  return body;
}

function showNotice(message, isError = false) {
  notice.textContent = message;
  notice.hidden = !message;
  notice.classList.toggle("is-error", isError);
}

function formatDueTime(value) {
  if (!value) return "No due time";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Due time set";

  return date.toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function dateToLocalInput(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 16);
}

function makeActionButton(label, className, onClick, accessibleLabel) {
  const button = document.createElement("button");
  button.className = className;
  button.type = "button";
  button.textContent = label;
  if (accessibleLabel) button.setAttribute("aria-label", accessibleLabel);
  button.addEventListener("click", onClick);
  return button;
}

function createTaskRow(task) {
  const row = document.createElement("li");
  row.className = "task-item";
  row.classList.toggle("is-complete", task.completed);

  const checkbox = document.createElement("input");
  checkbox.className = "task-check";
  checkbox.type = "checkbox";
  checkbox.checked = task.completed;
  checkbox.setAttribute(
    "aria-label",
    task.completed ? `Mark ${task.title} incomplete` : `Mark ${task.title} complete`,
  );
  checkbox.addEventListener("change", () => {
    changeTask(task.id, { completed: checkbox.checked });
  });

  const content = document.createElement("div");
  content.className = "task-content";

  const title = document.createElement("span");
  title.className = "task-title";
  title.textContent = task.title;
  content.append(title);

  const due = document.createElement("p");
  due.className = "task-due";
  due.textContent = task.due_at ? `Due ${formatDueTime(task.due_at)}` : "No due time";
  content.append(due);

  const actions = document.createElement("div");
  actions.className = "task-actions";
  actions.append(
    makeActionButton("Details", "secondary-button small-button", () => showTaskDetails(task.id)),
    makeActionButton("Edit", "secondary-button small-button", () => openEditTask(task.id)),
    makeActionButton("Delete", "delete-button", () => deleteTask(task.id), `Delete ${task.title}`),
  );

  row.append(checkbox, content, actions);
  return row;
}

function renderTasks() {
  taskList.replaceChildren();
  taskCount.textContent = String(tasks.length);

  if (isLoading) {
    emptyTitle.textContent = "Loading tasks";
    emptyCopy.textContent = `Getting patient ${activePatientId}'s list from FastAPI.`;
    emptyState.hidden = false;
    return;
  }

  if (loadFailed) {
    emptyTitle.textContent = "Tasks could not be loaded";
    emptyCopy.textContent = "Check the patient ID and make sure the FastAPI server is running.";
    emptyState.hidden = false;
    return;
  }

  if (tasks.length === 0) {
    emptyTitle.textContent = activeFilter === "all" ? "No tasks yet" : "No matching tasks";
    emptyCopy.textContent =
      activeFilter === "all"
        ? "Add a task above, or choose a different patient ID."
        : "Try another filter or add a new task.";
    emptyState.hidden = false;
    return;
  }

  emptyState.hidden = true;
  for (const task of tasks) taskList.append(createTaskRow(task));
}

async function loadTasks() {
  isLoading = true;
  loadFailed = false;
  renderTasks();

  try {
    tasks = await apiRequest(tasksUrl());
    showNotice("");
  } catch (error) {
    tasks = [];
    loadFailed = true;
    showNotice(error.message, true);
  } finally {
    isLoading = false;
    renderTasks();
  }
}

async function changeTask(taskId, changes) {
  try {
    await apiRequest(`/tasks/${taskId}`, {
      method: "PATCH",
      body: JSON.stringify(changes),
    });
    await loadTasks();
    showNotice("Task updated.");
  } catch (error) {
    renderTasks();
    showNotice(error.message, true);
  }
}

async function showTaskDetails(taskId) {
  try {
    const task = await apiRequest(`/tasks/${taskId}`);
    document.querySelector("#details-title").textContent = task.title;
    document.querySelector("#details-id").textContent = String(task.id);
    document.querySelector("#details-patient").textContent = String(task.patient_id);
    document.querySelector("#details-due").textContent = formatDueTime(task.due_at);
    document.querySelector("#details-status").textContent = task.completed ? "Complete" : "To do";
    detailsDialog.showModal();
  } catch (error) {
    showNotice(error.message, true);
  }
}

async function openEditTask(taskId) {
  try {
    const task = await apiRequest(`/tasks/${taskId}`);
    editTaskId.value = String(task.id);
    editTaskName.value = task.title;
    editTaskDue.value = dateToLocalInput(task.due_at);
    editTaskCompleted.checked = task.completed;
    editDialog.showModal();
  } catch (error) {
    showNotice(error.message, true);
  }
}

async function deleteTask(taskId) {
  try {
    await apiRequest(`/tasks/${taskId}`, { method: "DELETE" });
    await loadTasks();
    showNotice("Task deleted.");
  } catch (error) {
    showNotice(error.message, true);
  }
}

function updateFilterButtons() {
  for (const button of filters.querySelectorAll("[data-filter]")) {
    const selected = button.dataset.filter === activeFilter;
    button.classList.toggle("is-active", selected);
    button.setAttribute("aria-pressed", String(selected));
  }
}

patientForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const patientId = Number(patientInput.value);
  if (!Number.isSafeInteger(patientId) || patientId < 1) {
    showNotice("Enter a positive whole-number patient ID.", true);
    patientInput.focus();
    return;
  }

  activePatientId = patientId;
  activePatientLabel.textContent = String(patientId);
  activeFilter = "all";
  updateFilterButtons();
  await loadTasks();
  if (!loadFailed) showNotice(`Loaded patient ${patientId}'s task list.`);
});

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = titleInput.value.trim();
  if (!title) {
    showNotice("Enter a task name before adding it.", true);
    titleInput.focus();
    return;
  }

  const dueAt = dueInput.value ? new Date(dueInput.value).toISOString() : null;
  try {
    await apiRequest(`/patients/${activePatientId}/tasks`, {
      method: "POST",
      body: JSON.stringify({ title, due_at: dueAt }),
    });
    taskForm.reset();
    activeFilter = "all";
    updateFilterButtons();
    await loadTasks();
    showNotice("Task added.");
  } catch (error) {
    showNotice(error.message, true);
  }
});

editForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = editTaskName.value.trim();
  if (!title) {
    showNotice("A task needs a name.", true);
    editTaskName.focus();
    return;
  }

  const dueAt = editTaskDue.value ? new Date(editTaskDue.value).toISOString() : null;
  try {
    await apiRequest(`/tasks/${editTaskId.value}`, {
      method: "PUT",
      body: JSON.stringify({
        title,
        due_at: dueAt,
        completed: editTaskCompleted.checked,
      }),
    });
    editDialog.close();
    await loadTasks();
    showNotice("Task replaced.");
  } catch (error) {
    showNotice(error.message, true);
  }
});

filters.addEventListener("click", (event) => {
  const button = event.target.closest("[data-filter]");
  if (!button || button.dataset.filter === activeFilter) return;
  activeFilter = button.dataset.filter;
  updateFilterButtons();
  loadTasks();
});

document.querySelectorAll("[data-close-details]").forEach((button) => {
  button.addEventListener("click", () => detailsDialog.close());
});

document.querySelectorAll("[data-close-edit]").forEach((button) => {
  button.addEventListener("click", () => editDialog.close());
});

loadTasks();
