import pytest
from fastapi.testclient import TestClient
from sqlmodel import (
    Session, SQLModel, create_engine, select
)
from sqlalchemy.pool import StaticPool

from api.db import get_session
from api.todo.app import app
from api.todo.models import (
    TodoUser, TodoItem
)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_user(client: TestClient):
    response = client.post(
        "/users/grizelle"
    )
    data = response.json()

    assert response.status_code == 201
    assert data["name"] == "grizelle"
    assert data["id"] is not None


def test_get_users(session: Session, client: TestClient):
    users = [
        TodoUser(name="grizelle"),
        TodoUser(name="sombra"),
    ]
    for user in users:
        session.add(user)
    session.commit()

    resp = client.get(
        "/users"
    )
    data = resp.json()

    assert resp.status_code == 200
    assert isinstance(data["users"], list)
    assert len(data["users"]) == 2
    assert "grizelle" in [user["name"] for user in data["users"]]
    assert "sombra" in [user["name"] for user in data["users"]]


def test_post_todos(session: Session, client: TestClient):
    sombra = TodoUser(name="sombra")
    session.add(sombra)
    session.commit()

    resp = client.post(
        "/todos/sombra",
        json={
            "label": "Meow for food at 6 AM",
            "is_done": True
        }
    )
    data = resp.json()

    sombra = session.exec(select(TodoUser).where(
        TodoUser.name == "sombra")
    ).first()

    assert resp.status_code == 201
    assert len(sombra.todos) == 1
    assert data["label"] == "Meow for food at 6 AM"
    assert data["is_done"] == True
    assert data["id"] is not None


def test_put_todos(session: Session, client: TestClient):
    sombra = TodoUser(name="sombra")
    session.add(sombra)
    session.commit()
    session.refresh(sombra)
    todo = TodoItem(
        label="Hello, world!",
        is_done=False,
        user_id=sombra.id
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    session.refresh(sombra)

    resp = client.put(
        f"/todos/{todo.id}",
        json={
            "label": "Meow for food at 6 AM",
            "is_done": True
        }
    )
    data = resp.json()

    todo = session.get(TodoItem, todo.id)

    assert resp.status_code == 200
    assert data["label"] == "Meow for food at 6 AM"
    assert data["is_done"] == True
    assert data["id"] == todo.id


def test_delete_todos(session: Session, client: TestClient):
    sombra = TodoUser(name="sombra")
    session.add(sombra)
    session.commit()
    session.refresh(sombra)
    todo = TodoItem(
        label="Hello, world!",
        is_done=False,
        user_id=sombra.id
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    session.refresh(sombra)

    resp = client.delete(
        f"/todos/{todo.id}"
    )

    todo = session.get(TodoItem, todo.id)

    assert resp.status_code == 204
    assert todo is None


def test_delete_user(session: Session, client: TestClient):
    sombra = TodoUser(name="sombra")
    session.add(sombra)
    session.commit()
    session.refresh(sombra)
    todo = TodoItem(
        label="Hello, world!",
        is_done=False,
        user_id=sombra.id
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    session.refresh(sombra)

    grizelle = TodoUser(name="grizelle")
    session.add(grizelle)
    session.commit()
    session.refresh(grizelle)
    todo = TodoItem(
        label="Hello, world!",
        is_done=False,
        user_id=grizelle.id
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    session.refresh(grizelle)

    resp = client.delete(
        "/users/sombra"
    )

    sombra = session.get(TodoUser, sombra.id)
    todos = session.exec(select(TodoItem)).all()
    users = session.exec(select(TodoUser)).all()

    assert resp.status_code == 204
    assert sombra is None
    assert len(todos) == 1
    assert len(users) == 1
