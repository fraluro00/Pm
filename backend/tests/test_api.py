import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import ai as ai_module
import database
from main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    with TestClient(app) as c:
        yield c


def _login(client: TestClient):
    client.post("/api/auth/login", json={"username": "user", "password": "password"})


# --- health ---

def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# --- auth ---

def test_login_success(client):
    r = client.post("/api/auth/login", json={"username": "user", "password": "password"})
    assert r.status_code == 200
    assert r.json()["username"] == "user"
    assert "session" in r.cookies


def test_login_wrong_password(client):
    r = client.post("/api/auth/login", json={"username": "user", "password": "wrong"})
    assert r.status_code == 401


def test_me_unauthenticated(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_authenticated(client):
    _login(client)
    r = client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["username"] == "user"


def test_logout(client):
    _login(client)
    client.post("/api/auth/logout")
    r = client.get("/api/auth/me")
    assert r.status_code == 401


# --- board ---

def test_get_board_unauthenticated(client):
    r = client.get("/api/board")
    assert r.status_code == 401


def test_get_board_returns_seeded_data(client):
    _login(client)
    r = client.get("/api/board")
    assert r.status_code == 200
    data = r.json()
    assert len(data["columns"]) == 5
    assert len(data["cards"]) == 8
    assert data["columns"][0]["title"] == "Backlog"


def test_put_board_unauthenticated(client):
    r = client.put("/api/board", json={"columns": [], "cards": {}})
    assert r.status_code == 401


def test_put_board_persists(client):
    _login(client)
    board = {
        "columns": [{"id": "col-test", "title": "Test Column", "cardIds": ["card-a"]}],
        "cards": {"card-a": {"id": "card-a", "title": "Card A", "details": "some details"}},
    }
    r = client.put("/api/board", json=board)
    assert r.status_code == 200

    r = client.get("/api/board")
    data = r.json()
    assert len(data["columns"]) == 1
    assert data["columns"][0]["title"] == "Test Column"
    assert "card-a" in data["cards"]
    assert data["cards"]["card-a"]["title"] == "Card A"


def test_put_board_replaces_existing(client):
    _login(client)
    # First save
    client.put("/api/board", json={
        "columns": [{"id": "col-1", "title": "Old", "cardIds": []}],
        "cards": {},
    })
    # Replace with different data
    client.put("/api/board", json={
        "columns": [{"id": "col-2", "title": "New", "cardIds": []}],
        "cards": {},
    })
    r = client.get("/api/board")
    data = r.json()
    assert len(data["columns"]) == 1
    assert data["columns"][0]["title"] == "New"


# --- ai ---

def test_ai_test_unauthenticated(client):
    r = client.post("/api/ai/test")
    assert r.status_code == 401


def test_ai_test_returns_response(client, monkeypatch):
    _login(client)

    def fake_create(**kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="4"))]
        )

    monkeypatch.setattr(ai_module.client.chat.completions, "create", fake_create)
    r = client.post("/api/ai/test")
    assert r.status_code == 200
    assert r.json()["response"] == "4"


def test_ai_chat_no_board_update(client, monkeypatch):
    _login(client)

    def fake_create(**kwargs):
        content = json.dumps({"message": "Backlog has 2 cards.", "board_update": None})
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])

    monkeypatch.setattr(ai_module.client.chat.completions, "create", fake_create)
    r = client.post("/api/ai/chat", json={"user_message": "What's in Backlog?", "history": []})
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "Backlog has 2 cards."
    assert data["board_update"] is None


def test_ai_chat_with_board_update(client, monkeypatch):
    _login(client)

    new_board = {
        "columns": [
            {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-new"]},
            {"id": "col-discovery", "title": "Discovery", "cardIds": []},
            {"id": "col-progress", "title": "In Progress", "cardIds": []},
            {"id": "col-review", "title": "Review", "cardIds": []},
            {"id": "col-done", "title": "Done", "cardIds": []},
        ],
        "cards": {
            "card-new": {"id": "card-new", "title": "Test Card", "details": "Added by AI"}
        },
    }

    def fake_create(**kwargs):
        content = json.dumps({"message": "Added the card.", "board_update": new_board})
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])

    monkeypatch.setattr(ai_module.client.chat.completions, "create", fake_create)
    r = client.post("/api/ai/chat", json={"user_message": "Add Test Card to Backlog", "history": []})
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "Added the card."
    assert data["board_update"] is not None

    r = client.get("/api/board")
    board_data = r.json()
    assert "card-new" in board_data["cards"]
    assert board_data["cards"]["card-new"]["title"] == "Test Card"


def test_ai_chat_unauthenticated(client):
    r = client.post("/api/ai/chat", json={"user_message": "hello", "history": []})
    assert r.status_code == 401
