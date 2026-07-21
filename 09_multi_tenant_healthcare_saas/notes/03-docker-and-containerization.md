# Docker & Containerization

## The Problem

Your app runs on your machine. Your colleague's machine is different. The production server is different again.

```
"Works on my machine" → #1 cause of deployment issues
```

Docker solves this by packaging your app with its entire environment into a **container**.

## What is Docker?

Docker packages your application + all its dependencies into a portable unit.

```
┌─────────────────────────────────┐
│          Docker Container       │
│                                 │
│  ┌───────────────────────────┐  │
│  │    Your FastAPI App       │  │
│  ├───────────────────────────┤  │
│  │    Python 3.11           │  │
│  ├───────────────────────────┤  │
│  │    Ubuntu (minimal)       │  │
│  ├───────────────────────────┤  │
│  │    All pip packages       │  │
│  └───────────────────────────┘  │
│                                 │
│  Same environment everywhere    │
└─────────────────────────────────┘
```

## Dockerfile for FastAPI

A Dockerfile is a recipe for building your container:

```
# Start from official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your code
COPY . .

# Command to run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Docker Compose

A single app has multiple services (API, PostgreSQL, Redis). Docker Compose manages them together:

```
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:pass@db:5432/medapp
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
```

One command starts everything: `docker compose up`

## Why Docker for Multi-Tenant SaaS

| Benefit | Why it matters |
|---|---|
| Reproducibility | Dev, staging, production are identical |
| Isolation | Each service in its own container |
| Scaling | `docker compose up -d --scale api=5` |
| CI/CD | Same container built once, deployed everywhere |
| Rollback | Deploy old container if something breaks |

## The Multi-Container Architecture

```
┌─────────┐  ┌─────────┐  ┌─────────┐
│  API    │  │  API    │  │  API    │  ← Multiple API instances
│  (:8001)│  │  (:8002)│  │  (:8003)│
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     └────────────┼────────────┘
                  │
          ┌───────▼───────┐
          │  Nginx        │  ← Reverse proxy / load balancer
          │  (port 80)    │
          └───────┬───────┘
                  │
          ┌───────▼───────┐
          │  Internet     │
          └───────────────┘
```

## Key Insight

Docker doesn't just solve "works on my machine" — it creates a **deployment artifact** that's tested once and promoted through environments: dev → staging → production. No configuration drift, no environment-specific bugs.
