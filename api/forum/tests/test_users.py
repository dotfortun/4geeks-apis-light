import pytest
from fastapi.testclient import TestClient
from sqlmodel import (
    Session, SQLModel, create_engine, select
)
from sqlalchemy.pool import StaticPool

from api.db import get_session
from api.forum.app import app
from api.forum.models import ForumUser
from api.forum.routers.auth import get_password_hash


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


def test_get_users(session: Session, client: TestClient):
    from api.forum.routers.auth import get_password_hash
    users = [
        ForumUser(
            username="grizelle",
            email="grizelle@catemail.com",
            password=get_password_hash("blackhairties")
        ),
        ForumUser(
            username="sombra",
            email="sombra@catemail.com",
            password=get_password_hash("littleblueparrot")
        ),
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
    assert "grizelle" in [user["username"] for user in data["users"]]
    assert "sombra" in [user["username"] for user in data["users"]]


def test_create_users(session: Session, client: TestClient):
    resp = client.post(
        "/users",
        json={
            "username": "sombra",
            "email": "sombra@catemail.com",
            "password": "littleblueparrot"
        }
    )
    data = resp.json()

    sombra = session.exec(select(ForumUser)).first()

    assert resp.status_code == 201
    assert sombra.username == "sombra"
    assert sombra.email == "sombra@catemail.com"
    assert sombra.password != "littleblueparrot"
