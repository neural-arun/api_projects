from fastapi import FastAPI

from app.api.tasks import router as tasks_router

app = FastAPI(title="Patient Task Management API")
app.include_router(tasks_router)
