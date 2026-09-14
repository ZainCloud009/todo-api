import pytest
from fastapi.testclient import TestClient
from main import app, reset_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def run_around_tests():
    """Ensure in-memory state is clean before and after every test."""
    reset_store()
    yield
    reset_store()


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "docs" in data
    assert "health" in data


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_create_todo_success():
    payload = {"title": "Write Dockerfile", "description": "Multi-stage build for Python"}
    response = client.post("/todos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Write Dockerfile"
    assert data["description"] == "Multi-stage build for Python"
    assert data["completed"] is False
    assert "created_at" in data


def test_create_todo_missing_title():
    response = client.post("/todos", json={"description": "No title provided"})
    assert response.status_code == 422  # Validation error


def test_create_todo_empty_title():
    response = client.post("/todos", json={"title": ""})
    assert response.status_code == 422  # Validation error (min_length=1)


def test_list_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_list_todos_populated_and_filter():
    client.post("/todos", json={"title": "Task 1"})
    client.post("/todos", json={"title": "Task 2"})
    client.patch("/todos/1/done")

    # List all
    response = client.get("/todos")
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Filter completed
    response_completed = client.get("/todos?completed=true")
    assert response_completed.status_code == 200
    assert len(response_completed.json()) == 1
    assert response_completed.json()[0]["id"] == 1

    # Filter incomplete
    response_pending = client.get("/todos?completed=false")
    assert response_pending.status_code == 200
    assert len(response_pending.json()) == 1
    assert response_pending.json()[0]["id"] == 2


def test_get_todo_by_id():
    created = client.post("/todos", json={"title": "Single Task"}).json()
    todo_id = created["id"]

    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Single Task"


def test_get_todo_not_found():
    response = client.get("/todos/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_mark_todo_done_success():
    created = client.post("/todos", json={"title": "Pending Task"}).json()
    todo_id = created["id"]

    response = client.patch(f"/todos/{todo_id}/done")
    assert response.status_code == 200
    assert response.json()["completed"] is True

    # Verify persistent in list
    verify = client.get(f"/todos/{todo_id}").json()
    assert verify["completed"] is True


def test_mark_todo_done_not_found():
    response = client.patch("/todos/999/done")
    assert response.status_code == 404


def test_update_todo():
    created = client.post("/todos", json={"title": "Initial Title"}).json()
    todo_id = created["id"]

    response = client.put(f"/todos/{todo_id}", json={"title": "Updated Title", "completed": True})
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "Updated Title"
    assert updated["completed"] is True


def test_delete_todo():
    created = client.post("/todos", json={"title": "To be deleted"}).json()
    todo_id = created["id"]

    delete_resp = client.delete(f"/todos/{todo_id}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/todos/{todo_id}")
    assert get_resp.status_code == 404

    delete_again = client.delete(f"/todos/{todo_id}")
    assert delete_again.status_code == 404
