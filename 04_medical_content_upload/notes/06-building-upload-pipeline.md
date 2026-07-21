# Building the Complete Upload Pipeline

This note combines everything: upload → validate → store → log → background task.

## The Full Workflow

```
Client uploads file
    │
    ▼
1. RECEIVE — UploadFile reads the stream
    │
    ▼
2. VALIDATE — MIME type, size, malware scan
    │
    ▼
3. STORE — Save to disk with UUID name
    │
    ▼
4. RECORD — Save metadata (path, size, type, patient_id) to database
    │
    ▼
5. RETURN — Send response immediately
    │
    ▼
6. BACKGROUND — Generate thumbnail, send notification (after response)
```

## 1. Project Setup

```
medical_upload/
├── main.py           # FastAPI app
├── database.py       # SQLModel setup
├── models.py         # File metadata model
├── schemas.py        # Pydantic response models
├── storage.py        # File save/read logic
└── uploads/          # Stored files (outside web root)
```

## 2. Database Model

```python
# models.py
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class UploadedFile(SQLModel, table=True):
    __tablename__ = "uploaded_files"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    original_filename: str
    stored_filename: str
    file_path: str
    file_size: int
    mime_type: str
    patient_id: int | None = None
    uploaded_at: datetime = Field(default_factory=datetime.now)
```

## 3. Validation Logic

```python
# storage.py
import magic
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_SIZE = 50 * 1024 * 1024  # 50 MB

async def validate_file(file: UploadFile):
    # Check MIME type via magic bytes
    header = await file.read(2048)
    mime_type = magic.from_buffer(header, mime=True)
    await file.seek(0)

    if mime_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type {mime_type} not allowed")

    # Check size
    content = await file.read()
    file_size = len(content)
    await file.seek(0)

    if file_size > MAX_SIZE:
        raise HTTPException(413, f"File too large ({file_size} bytes > {MAX_SIZE})")

    return mime_type, file_size
```

## 4. Storage Logic

```python
# storage.py (continued)
async def save_file(file: UploadFile, mime_type: str) -> tuple[str, str, str]:
    ext = Path(file.filename).suffix if file.filename else ".bin"
    stored_name = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / stored_name

    content = await file.read()
    file_path.write_bytes(content)

    return stored_name, str(file_path), mime_type
```

## 5. Background Task

```python
# tasks.py
from pathlib import Path

def generate_thumbnail(filepath: str, thumbnail_dir: str = "thumbnails"):
    Path(thumbnail_dir).mkdir(exist_ok=True)
    thumb_path = Path(thumbnail_dir) / Path(filepath).name

    try:
        from PIL import Image
        img = Image.open(filepath)
        img.thumbnail((200, 200))
        img.save(thumb_path)
        print(f"Thumbnail saved: {thumb_path}")
    except Exception as e:
        print(f"Thumbnail failed: {e}")

def log_upload_to_audit(file_id: str, patient_id: int, filename: str):
    from datetime import datetime
    with open("audit.log", "a") as f:
        f.write(f"{datetime.now().isoformat()}|UPLOAD|{file_id}|{patient_id}|{filename}\n")
```

## 6. The Upload Endpoint (Everything Together)

```python
# main.py
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends
from sqlmodel import SQLModel, Session, create_engine
from models import UploadedFile
from storage import validate_file, save_file
from tasks import generate_thumbnail, log_upload_to_audit
from datetime import datetime

app = FastAPI()
engine = create_engine("sqlite:///medical_uploads.db")
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.post("/upload/")
async def upload_medical_file(
    file: UploadFile = File(),
    tasks: BackgroundTasks = None,
    patient_id: int = None,
    session: Session = Depends(get_session),
):
    # 1. VALIDATE
    mime_type, file_size = await validate_file(file)

    # 2. STORE
    stored_name, file_path, _ = await save_file(file, mime_type)

    # 3. RECORD in database
    db_file = UploadedFile(
        original_filename=file.filename or "unnamed",
        stored_filename=stored_name,
        file_path=file_path,
        file_size=file_size,
        mime_type=mime_type,
        patient_id=patient_id,
    )
    session.add(db_file)
    session.commit()
    session.refresh(db_file)

    # 4. BACKGROUND TASKS (run after response)
    tasks.add_task(generate_thumbnail, file_path)
    tasks.add_task(log_upload_to_audit, db_file.id, patient_id, file.filename)

    # 5. RESPOND immediately
    return {
        "id": db_file.id,
        "filename": file.filename,
        "mime_type": mime_type,
        "file_size": file_size,
        "uploaded_at": db_file.uploaded_at.isoformat(),
    }
```

## 7. List and Download Endpoints

```python
# main.py (continued)
from fastapi.responses import FileResponse

@app.get("/files/")
def list_files(session: Session = Depends(get_session)):
    files = session.query(UploadedFile).all()
    return [
        {
            "id": f.id,
            "filename": f.original_filename,
            "mime_type": f.mime_type,
            "file_size": f.file_size,
            "patient_id": f.patient_id,
            "uploaded_at": f.uploaded_at.isoformat(),
        }
        for f in files
    ]

@app.get("/files/{file_id}/download")
def download_file(file_id: str, session: Session = Depends(get_session)):
    db_file = session.get(UploadedFile, file_id)
    if not db_file:
        raise HTTPException(404, "File not found")

    return FileResponse(
        path=db_file.file_path,
        filename=db_file.original_filename,
        media_type=db_file.mime_type,
    )
```

## Cloud Storage (S3 Alternative)

For production, replace local disk with S3-compatible storage:

```python
# storage_s3.py
import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client("s3")
BUCKET = "medical-uploads"

async def save_to_s3(file: UploadFile, key: str) -> str:
    content = await file.read()
    s3_client.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=content,
        ContentType=file.content_type,
    )
    return f"s3://{BUCKET}/{key}"

async def get_from_s3(key: str) -> bytes:
    response = s3_client.get_object(Bucket=BUCKET, Key=key)
    return response["Body"].read()
```

## Summary: The Pipeline at a Glance

```
Receive  →  Validate  →  Store  →  Record  →  Respond  →  Background
                           │                       │
                     Local disk or S3         File metadata in DB
```

Each stage is a separate concern. Keep them in separate functions/files. Test each one independently.

> Reference: https://fastapi.tiangolo.com/tutorial/request-files/
