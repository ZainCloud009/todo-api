# To-Do List API & Containerized DevOps Pipeline

[![CI Pipeline](https://github.com/ZainCloud009/todo-api/actions/workflows/ci.yml/badge.svg)](https://github.com/ZainCloud009/todo-api/actions/workflows/ci.yml)
![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-enabled-2496ED.svg?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A clean, production-ready RESTful To-Do List API built with **FastAPI**, containerized using **Docker** following security best practices (non-root execution, minimal layers, health checking), and automated via **GitHub Actions** CI.

---

## Table of Contents

- [Features & Tech Stack](#features--tech-stack)
- [Project Structure](#project-structure)
- [Getting Started (Local)](#getting-started-local)
- [Running with Docker](#running-with-docker)
- [Running with Docker Compose](#running-with-docker-compose)
- [Interactive API Documentation](#interactive-api-documentation)
- [API Reference & Examples](#api-reference--examples)
- [Running Tests](#running-tests)
- [CI/CD Pipeline](#cicd-pipeline)
- [Reflection](#reflection)

---

## Features & Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12) - High performance, type hints, and automatic OpenAPI documentation.
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/) - Request payload parsing and schema enforcement.
- **Server**: [Uvicorn](https://www.uvicorn.org/) - ASGI web server.
- **Storage**: Thread-safe in-memory store (no external database dependencies required).
- **Containerization**: Multi-layer, slim Docker image running as a non-privileged `appuser`.
- **Testing**: [pytest](https://docs.pytest.org/) and FastAPI `TestClient` (HTTPX).
- **CI/CD**: GitHub Actions workflow running automated unit tests and Docker builds on every push/PR.

---

## Project Structure

```text
todo-api/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI workflow (Tests + Docker build)
├── tests/
│   ├── __init__.py
│   └── test_main.py           # Automated unit and integration test suite
├── .dockerignore              # Excludes unnecessary files from Docker build context
├── .gitignore                 # Git ignore rules for Python, virtualenv, and caches
├── compose.yaml               # Docker Compose configuration for local orchestration
├── Dockerfile                 # Hardened, non-root Dockerfile with health checks
├── main.py                    # FastAPI application, data models, and route handlers
├── requirements.txt           # Application and testing dependencies
└── README.md                  # Project documentation & reflection
```

---

## Getting Started (Local)

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- `pip` package manager

### 1. Clone the repository
```bash
git clone https://github.com/ZainCloud009/todo-api.git
cd todo-api
```

### 2. Create and activate a virtual environment
```bash
# On Linux/macOS:
python3 -m venv .venv
source .venv/bin/activate

# On Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the development server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
The API will be available at: `http://localhost:8000`

---

## Running with Docker

The application includes a hardened Dockerfile using `python:3.12-slim` that creates and runs under an unprivileged user (`appuser`).

### 1. Build the Docker image
```bash
docker build -t todo-api:latest .
```

### 2. Run the Docker container
```bash
docker run -d -p 8000:8000 --name todo-api-app todo-api:latest
```

### 3. Check container logs & status
```bash
docker ps
docker logs -f todo-api-app
```

### 4. Stop and remove container
```bash
docker stop todo-api-app
docker rm todo-api-app
```

---

## Running with Docker Compose

For single-command startup, use Docker Compose:

```bash
# Start container in detached mode
docker compose up -d --build

# View logs
docker compose logs -f

# Stop and tear down
docker compose down
```

---

## Interactive API Documentation

Once the server is running, FastAPI provides built-in interactive documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) (Allows executing live requests directly from the browser)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Reference & Examples

### Summary of Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Welcome message and API overview links |
| `GET` | `/health` | Health check endpoint for orchestrators (Kubernetes / Docker) |
| `POST` | `/todos` | Add a new to-do task |
| `GET` | `/todos` | List all tasks (supports `?completed=true|false` query filter) |
| `GET` | `/todos/{id}` | Get a single task by ID |
| `PATCH` | `/todos/{id}/done` | Mark a task as completed |
| `PUT` | `/todos/{id}` | Update task details (title, description, completed) |
| `DELETE` | `/todos/{id}` | Delete a task |

---

### 1. Health Check
Checks service availability.

```bash
curl -X GET http://localhost:8000/health
```

**Response (`200 OK`)**:
```json
{
  "status": "healthy",
  "timestamp": "2026-09-14T09:15:00.000000+00:00"
}
```

---

### 2. Add a Task (`POST /todos`)
Creates a new task.

```bash
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Set up CI/CD pipeline",
    "description": "Configure GitHub Actions to build Docker image"
  }'
```

**Response (`201 Created`)**:
```json
{
  "id": 1,
  "title": "Set up CI/CD pipeline",
  "description": "Configure GitHub Actions to build Docker image",
  "completed": false,
  "created_at": "2026-09-14T09:16:12.345678+00:00"
}
```

---

### 3. List All Tasks (`GET /todos`)
Retrieves all tasks stored in memory.

```bash
# Retrieve all tasks
curl -X GET http://localhost:8000/todos

# Filter for only completed tasks
curl -X GET "http://localhost:8000/todos?completed=true"

# Filter for only pending tasks
curl -X GET "http://localhost:8000/todos?completed=false"
```

**Response (`200 OK`)**:
```json
[
  {
    "id": 1,
    "title": "Set up CI/CD pipeline",
    "description": "Configure GitHub Actions to build Docker image",
    "completed": false,
    "created_at": "2026-09-14T09:16:12.345678+00:00"
  }
]
```

---

### 4. Get a Task by ID (`GET /todos/{id}`)

```bash
curl -X GET http://localhost:8000/todos/1
```

**Response (`200 OK`)**:
```json
{
  "id": 1,
  "title": "Set up CI/CD pipeline",
  "description": "Configure GitHub Actions to build Docker image",
  "completed": false,
  "created_at": "2026-09-14T09:16:12.345678+00:00"
}
```

---

### 5. Mark Task as Done (`PATCH /todos/{id}/done`)
Marks the specified task as completed.

```bash
curl -X PATCH http://localhost:8000/todos/1/done
```

**Response (`200 OK`)**:
```json
{
  "id": 1,
  "title": "Set up CI/CD pipeline",
  "description": "Configure GitHub Actions to build Docker image",
  "completed": true,
  "created_at": "2026-09-14T09:16:12.345678+00:00"
}
```

---

### 6. Delete a Task (`DELETE /todos/{id}`)

```bash
curl -X DELETE http://localhost:8000/todos/1
```

**Response (`204 No Content`)**

---

## Running Tests

Automated tests are written with `pytest` and test all endpoints, query parameters, validation rules, and error conditions.

```bash
# Run pytest with verbose output
pytest -v
```

Expected output:
```text
tests/test_main.py::test_root_endpoint PASSED
tests/test_main.py::test_health_endpoint PASSED
tests/test_main.py::test_create_todo_success PASSED
tests/test_main.py::test_create_todo_missing_title PASSED
tests/test_main.py::test_create_todo_empty_title PASSED
tests/test_main.py::test_list_todos_empty PASSED
tests/test_main.py::test_list_todos_populated_and_filter PASSED
tests/test_main.py::test_get_todo_by_id PASSED
tests/test_main.py::test_get_todo_not_found PASSED
tests/test_main.py::test_mark_todo_done_success PASSED
tests/test_main.py::test_mark_todo_done_not_found PASSED
tests/test_main.py::test_update_todo PASSED
tests/test_main.py::test_delete_todo PASSED
```

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) is triggered on every `push` and `pull_request` to the `main` branch.

### Pipeline Stages:
1. **`test` Job**:
   - Checks out repository code.
   - Sets up Python 3.12 environment with pip caching.
   - Installs project dependencies.
   - Runs `pytest -v` to ensure test assertions pass before building.
2. **`build-docker` Job** (Depends on `test`):
   - Sets up Docker Buildx.
   - Builds the Docker image utilizing GitHub Actions layer caching (`type=gha`) for fast builds.
   - Spins up the built container and runs an automated smoke check against `http://localhost:8000/health` to confirm the container runs properly in an isolated environment.

---

## Reflection

### 1. What was the trickiest part of this for you?
The trickiest part was balancing **simplicity** with **production-grade DevOps standards**. While writing an in-memory To-Do API is straightforward, setting up the container and CI pipeline properly requires careful decisions:
- **Container Security & Hardening**: Rather than defaulting to running as `root` (which is a common vulnerability in simple take-home projects), I created a non-privileged `appuser` and `appgroup`, adjusted file permissions, and enforced non-root execution.
- **Lightweight Health Checking**: Minimal `slim` images do not bundle `curl` or `wget`. Instead of adding bloated dependencies or running insecure utilities, I implemented the container `HEALTHCHECK` using Python's built-in `urllib.request`. This kept the image lightweight (~150MB) and dependency-free while fulfilling orchestrator requirements.
- **Thread Safety in In-Memory State**: In multi-threaded ASGI servers, in-memory global data structures can encounter race conditions during concurrent requests. Implementing a thread lock (`threading.Lock`) ensured thread safety without complicating the architecture with a full database.

### 2. Why you made the choices you did?
- **Python with FastAPI**:
  - FastAPI is modern, typed, and clean. It leverages Pydantic for validation and serialization, minimizing boilerplate code.
  - It automatically generates interactive Swagger documentation at `/docs`, which makes exploring and verifying endpoints effortless during a live interview walkthrough.
- **`python:3.12-slim` as Base Image**:
  - Full Python base images often exceed 1GB, whereas Alpine images can introduce obscure compatibility quirks with C-extensions (`musl` vs `glibc`). The `slim` image provides an optimal balance: small footprint, fast build times, and high reliability.
- **Docker Layer Caching**:
  - Copying `requirements.txt` and installing dependencies before copying `main.py` ensures that subsequent code modifications reuse cached layers, drastically speeding up CI execution.
- **Two-Stage GitHub Actions Pipeline**:
  - Running unit tests as a prerequisite step before building the Docker image adheres to standard CI practices: fail fast on code defects before spending compute resources building containers.

### 3. If you had another day, what would you improve or do differently?
If I had additional time, I would expand the project in the following areas:
1. **Persistent Database & Migrations**:
   - Replace in-memory storage with **PostgreSQL** or **SQLite** using **SQLAlchemy** or **SQLModel**, paired with **Alembic** for schema migrations.
   - Update `compose.yaml` to include a managed database service container and volume persistence.
2. **Authentication & Multi-User Isolation**:
   - Implement JWT-based authentication (OAuth2 with password flow) so tasks belong to individual authenticated users rather than a single shared store.
3. **DevOps Observability & Metrics**:
   - Instrument the application with **Prometheus** metrics (`/metrics`) using `prometheus-fastapi-instrumentator` to track request rates, latencies, and error codes.
   - Add structured JSON logging (e.g., using `structlog`) to facilitate log aggregation in tools like Grafana Loki or AWS CloudWatch.
4. **Cloud Deployment & CD**:
   - Extend GitHub Actions with a Continuous Deployment (CD) job targeting a cloud environment like **Google Cloud Run**, **AWS ECS/Fargate**, or a lightweight Kubernetes cluster (K3s/Minikube) using Helm charts.
