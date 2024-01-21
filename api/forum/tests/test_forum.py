from typing import List
import pytest
from fastapi.testclient import TestClient
from sqlmodel import (
    Session, SQLModel, create_engine, select
)
from sqlalchemy.pool import StaticPool

from api.db import get_session
from api.forum.app import app
from api.forum.models import ForumPost, ForumThread, ForumUser
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


def get_auth_header(client: TestClient, user: str, passwd: str):
    resp = client.post(
        "/auth/token",
        data={
            "username": user,
            "password": passwd
        }
    )
    data = resp.json()
    return {
        "Authorization": f"""Bearer {data["access_token"]}"""
    }


def gen_users(session: Session) -> List[ForumUser]:
    db_users = [
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
        ForumUser(
            username="nekobasu",
            email="nekobasu@catemail.com",
            password=get_password_hash("greendragonstuffy")
        ),
    ]
    session.add_all(db_users)
    session.commit()
    for user in db_users:
        session.refresh(user)
    return db_users


def gen_threads(session: Session, db_users) -> List[ForumThread]:
    db_threads = [
        ForumThread(
            user_id=user.id,
            title="Cat business",
            content="A discussion about cat business"
        )
        for user in db_users
    ]
    session.add_all(db_threads)
    session.commit()
    for thread in db_threads:
        session.refresh(thread)
    return db_threads


def gen_posts(session: Session, db_threads) -> List[ForumPost]:
    db_posts = [
        ForumPost(
            user_id=thread.user_id,
            thread_id=thread.id,
            content="A reply about cat business"
        )
        for thread in db_threads
    ]
    session.add_all(db_posts)
    session.commit()
    for post in db_posts:
        session.refresh(post)
    return db_posts


def test_get_users(session: Session, client: TestClient):
    db_users = gen_users(session)

    resp = client.get(
        "/users"
    )
    data = resp.json()

    assert resp.status_code == 200
    assert isinstance(data["users"], list)
    assert len(data["users"]) == len(db_users)
    assert "grizelle" in [user["username"] for user in data["users"]]
    assert "sombra" in [user["username"] for user in data["users"]]

    resp = client.get(
        "/users/sombra"
    )
    data = resp.json()

    assert resp.status_code == 200
    assert isinstance(data, dict)
    assert data["username"] == "sombra"
    assert data["email"] == "sombra@catemail.com"
    assert data["posts"] == []
    assert data["threads"] == []


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


def test_read_threads(session: Session, client: TestClient):
    db_users = gen_users(session)
    db_threads = gen_threads(session, db_users)

    resp = client.get("/threads")
    data = resp.json()

    assert resp.status_code == 200
    assert len(data["threads"]) == len(db_threads)

    resp = client.get("/threads/1")
    data = resp.json()

    assert resp.status_code == 200
    assert data["title"] == "Cat business"
    assert data["content"] == "A discussion about cat business"


def test_create_threads(session: Session, client: TestClient):
    gen_users(session)

    resp = client.post(
        "/threads",
        json={
            "title": "A post that a cat would make.",
            "content": "You know, a post about cat stuff."
        }
    )

    assert resp.status_code == 401

    headers = get_auth_header(
        client, "grizelle", "blackhairties"
    )
    resp = client.post(
        "/threads",
        headers=headers,
        json={
            "title": "It's 5:05pm.",
            "content": "I'm starving, and have never known food."
        }
    )
    data = resp.json()

    assert resp.status_code == 201
    assert data["title"] == "It's 5:05pm."
    assert data["content"] == "I'm starving, and have never known food."
    assert data["user"]["username"] == "grizelle"
    assert len(data["posts"]) == 0

    resp = client.post(
        "/threads",
        headers=headers,
        json={
            "invalid": "json body"
        }
    )
    data = resp.json()

    assert resp.status_code == 422
    assert "detail" in data.keys()


def test_update_threads(session: Session, client: TestClient):
    pass


def test_read_posts(session: Session, client: TestClient):
    db_posts = gen_posts(session, gen_users(session))


def test_create_posts(session: Session, client: TestClient):
    pass


def test_update_posts(session: Session, client: TestClient):
    pass
