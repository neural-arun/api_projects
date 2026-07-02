# Why Do We Need a Database?

## The Problem With In-Memory Storage

In Build 1, you stored tasks like this:

```python
tasks: list[dict] = []
next_id: int = 1
```

Three massive problems with this:

### 1. Data disappears when server restarts

```bash
# Start server, create a task
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" \
  -d '{"title": "Give insulin", "patient_name": "Ravi"}'
# → Task created successfully

# Ctrl+C the server, restart it
# → All tasks gone. Forever.
```

This is called **volatile storage**. The moment your Python process stops, that list is erased from RAM. In a real hospital, you can't lose patient data every time there's a server restart.

### 2. No concurrent access safety

If two nurses mark tasks as complete at the exact same millisecond:

```python
# Nurse A and Nurse B both hit this code simultaneously
for index, task in enumerate(tasks):
    if task["id"] == 5:
        tasks.pop(index)  # Both try to remove the same task
```

You can get corrupted data, crashed server, or both. This is called a **race condition**. PostgreSQL handles this correctly out of the box.

### 3. Can't search or filter efficiently

```python
# Find all notes containing "fever" — you'd have to loop through everything
fever_notes = [t for t in tasks if "fever" in t.get("description", "")]
```

This works for 10 tasks. For 10,000 patient notes, it's slow. For 1 million, it's unusable. Databases have **indexes** that make search instant.

## What a Database Gives You

| Need | In-Memory List | PostgreSQL Database |
|---|---|---|
| Survives restart | ❌ Gone | ✅ Stays on disk |
| Concurrent safety | ❌ Race conditions | ✅ ACID transactions |
| Search speed | ❌ Full scan | ✅ Indexes |
| Relationships | ❌ Manual code | ✅ Foreign keys, JOINs |
| Data integrity | ❌ Rely on your code | ✅ Constraints, types |
| Rollback on error | ❌ Can't undo | ✅ Transactions |

## Real-Life Analogy

Think of in-memory storage like writing patient info on a whiteboard:
- Looks fine while you're in the room
- Someone erases it accidentally? Lost forever
- Two people writing at once? Mess

A database is like a hospital filing system:
- Paper records in a fireproof cabinet
- Multiple staff can access without losing files
- Indexed by patient ID, name, ailment
- You can find "all patients with fever" in seconds

## The Bottom Line

Build 1 taught you API logic. Build 2 teaches you **persistence** — the ability to store data permanently and retrieve it reliably. This is the difference between a demo and a real system.

Next up: setting up PostgreSQL and writing your first SQL.
