from datetime import datetime, timezone
import threading
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="To-Do List APP API",
    description="A lightweight, containerized To-Do List API built for DevOps & Cloud demonstration.",
    version="1.0.0",
)

# In-memory data store with thread lock for safety
_lock = threading.Lock()
_todos: Dict[int, dict] = {}
_id_counter: int = 0


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="The title of the task")
    description: Optional[str] = Field(default=None, max_length=1000, description="Optional details about the task")


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = Field(default=None)


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: str


def reset_store():
    """Helper method to reset in-memory store (used primarily during testing)."""
    global _todos, _id_counter
    with _lock:
        _todos.clear()
        _id_counter = 0


@app.get("/", tags=["General"])
def root():
    """Welcome endpoint with API details and documentation link."""
    return {
        "message": "Welcome to the To-Do List API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["General"])
def health_check():
    """Health check endpoint for container orchestrators and monitoring tools."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post(
    "/todos",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Todos"],
    summary="Add a new task",
)
def create_todo(payload: TodoCreate):
    """Create and store a new to-do task."""
    global _id_counter
    with _lock:
        _id_counter += 1
        new_todo = {
            "id": _id_counter,
            "title": payload.title.strip(),
            "description": payload.description.strip() if payload.description else None,
            "completed": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        _todos[_id_counter] = new_todo
        return new_todo


@app.get(
    "/todos",
    response_model=List[TodoResponse],
    tags=["Todos"],
    summary="List tasks",
)
def list_todos(
    completed: Optional[bool] = Query(
        default=None,
        description="Filter tasks by completion status (true/false)",
    )
):
    """Retrieve all to-do tasks, with optional filtering by completed status."""
    with _lock:
        tasks = list(_todos.values())
        if completed is not None:
            tasks = [t for t in tasks if t["completed"] == completed]
        return tasks


@app.get(
    "/todos/{todo_id}",
    response_model=TodoResponse,
    tags=["Todos"],
    summary="Get a task by ID",
)
def get_todo(todo_id: int):
    """Retrieve a single task by its unique identifier."""
    with _lock:
        todo = _todos.get(todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )
        return todo


@app.patch(
    "/todos/{todo_id}/done",
    response_model=TodoResponse,
    tags=["Todos"],
    summary="Mark a task as done",
)
def mark_todo_done(todo_id: int):
    """Mark an existing task as completed."""
    with _lock:
        todo = _todos.get(todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )
        todo["completed"] = True
        return todo


@app.put(
    "/todos/{todo_id}",
    response_model=TodoResponse,
    tags=["Todos"],
    summary="Update task details",
)
def update_todo(todo_id: int, payload: TodoUpdate):
    """Update title, description, or completed status of a task."""
    with _lock:
        todo = _todos.get(todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )
        if payload.title is not None:
            todo["title"] = payload.title.strip()
        if payload.description is not None:
            todo["description"] = payload.description.strip()
        if payload.completed is not None:
            todo["completed"] = payload.completed
        return todo


@app.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Todos"],
    summary="Delete a task",
)
def delete_todo(todo_id: int):
    """Delete a task by ID."""
    with _lock:
        if todo_id not in _todos:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )
        del _todos[todo_id]
        return None
