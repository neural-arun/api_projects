from pathlib import Path

from fastapi import FastAPI

from app.api.tasks import router as tasks_router

app = FastAPI(title="Patient Task Management API")
app.include_router(tasks_router)
frontend_directory = Path(__file__).resolve().parent.parent / "frontend"
app.frontend("/", directory=str(frontend_directory))
