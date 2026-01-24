import pytest
from fastapi.testclient import TestClient

from api import app
from models import Todo

BASE_URL = "http://localhost:8000/api/v1"

client = TestClient(app)


def test_should_return_ok():
    response = client.get(f"{BASE_URL}/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_todo_with_valide_data_should_succeed(mock_db_session):
    def refresh(obj):
        obj.id = 1

    mock_db_session.refresh = refresh
    payload = {"title": "Test task"}
    response = client.post(f"{BASE_URL}/todos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == payload["title"]
    assert data["status"] == "new"
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called()


@pytest.mark.parametrize(
    "payload,message",
    [
        ({"titles": "Learn coding"}, "title: Field required"),
        ({"title": "RX"}, "title: String should have at least 3 characters"),
    ],
)
def test_create_todo_with_invalid_data_should_fail(payload, message):
    response = client.post(f"{BASE_URL}/todos", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == message


def test_get_existing_todo_should_succeed(mock_db_session):
    mock_db_session.get.return_value = Todo(id=1, title="Test task", status="new")
    response = client.get(f"{BASE_URL}/todos/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Test task"
    assert response.json()["status"] == "new"


def test_get_non_existing_todo_should_fail(mock_db_session):
    mock_db_session.get.return_value = None
    response = client.get(f"{BASE_URL}/todos/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_delete_existing_todo_should_succeed(mock_db_session):
    mock_db_session.get.return_value = Todo(id=1, title="Test task", status="new")
    response = client.delete(f"{BASE_URL}/todos/1")
    assert response.status_code == 204
    mock_db_session.delete.assert_called()
    mock_db_session.commit.assert_called()


def test_delete_non_existing_todo_should_fail(mock_db_session):
    mock_db_session.get.return_value = None
    response = client.delete(f"{BASE_URL}/todos/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_todo_with_valid_data_should_succeed(mock_db_session):
    mock_db_session.get.return_value = Todo(id=1, title="Test task", status="new")
    payload = {"title": "Learn coding", "status": "doing"}
    response = client.put(f"{BASE_URL}/todos/1", json=payload)
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["title"] == payload["title"]
    assert response.json()["status"] == payload["status"]
    mock_db_session.commit.assert_called()


def test_update_non_existing_todo_should_fail(mock_db_session):
    mock_db_session.get.return_value = None
    payload = {"title": "Learn coding", "status": "doing"}
    response = client.put(f"{BASE_URL}/todos/1", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.parametrize(
    "payload,message",
    [
        ({"title": "Learn coding"}, "status: Field required"),
        (
            {"title": "Learn coding", "status": "close"},
            "status: Input should be 'new', 'doing' or 'completed'",
        ),
    ],
)
def test_update_doto_with_invalid_data_should_fail(payload, message):
    response = client.put(f"{BASE_URL}/todos/1", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == message


def test_get_all_todos_should_succeed(mock_db_session):
    mock_db_session.exec.return_value.all.return_value = [
        Todo(id=1, title="Test task", status="new"),
        Todo(id=2, title="Learn coding", status="doing"),
    ]

    response = client.get(f"{BASE_URL}/todos")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_todos_filtered_by_status(mock_db_session):
    response = client.get(f"{BASE_URL}/todos?status=new")
    assert response.status_code == 200
    mock_db_session.exec.assert_called()
    stmt = mock_db_session.exec.call_args[0][0]
    assert "WHERE" in str(stmt)


def test_complete_existing_todo_should_succeed(mock_db_session):
    mock_db_session.get.return_value = Todo(id=1, title="Test task", status="doing")
    response = client.post(f"{BASE_URL}/todos/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["status"] == "completed"
    mock_db_session.commit.assert_called()


def test_complete_non_existing_todo_should_fail(mock_db_session):
    mock_db_session.get.return_value = None
    response = client.post(f"{BASE_URL}/todos/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
