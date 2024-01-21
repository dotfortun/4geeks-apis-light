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


def test_delete(session: Session, client: TestClient):
    db_users = gen_users(session)
    db_threads = gen_threads(session, db_users)
    db_posts = gen_posts(session, db_threads)

    for user in db_users:
        match(user.username):
            case "grizelle":
                # Test deleting ForumUsers
                # Count threads and posts before starting
                db_threads = session.exec(
                    select(ForumThread).where(ForumThread.user_id == user.id)
                ).all()
                thread_count = len(db_threads)
                db_posts = session.exec(
                    select(ForumPost).where(ForumPost.user_id == user.id)
                ).all()
                post_count = len(db_posts)

                headers = get_auth_header(
                    client, "grizelle", "blackhairties"
                )
                resp = client.delete(
                    f"/users/{user.id}",
                    headers=headers
                )
                db_user = session.get(ForumUser, user.id)
                db_threads = session.exec(
                    select(ForumThread).where(ForumThread.user_id == user.id)
                ).all()
                db_posts = session.exec(
                    select(ForumPost).where(ForumPost.user_id == user.id)
                ).all()

                assert resp.status_code == 204
                assert db_user is None
                assert len(db_threads) == thread_count - 1
                assert len(db_posts) == post_count - 1
            case "sombra":
                # Test deleting ForumThreads
                # Count threads and posts before starting
                db_threads = session.exec(
                    select(ForumThread).where(ForumThread.user_id == user.id)
                ).all()
                thread_count = len(db_threads)
                db_posts = session.exec(
                    select(ForumPost).where(ForumPost.user_id == user.id)
                ).all()
                post_count = len(db_posts)

                headers = get_auth_header(
                    client, "sombra", "littleblueparrot"
                )
                resp = client.delete(
                    f"/threads/{user.threads[0].id}",
                    headers=headers
                )
                db_user = session.get(ForumUser, user.id)
                db_threads = session.exec(
                    select(ForumThread).where(ForumThread.user_id == user.id)
                ).all()
                db_posts = session.exec(
                    select(ForumPost).where(ForumPost.user_id == user.id)
                ).all()

                assert resp.status_code == 204
                assert db_user is not None
                assert len(db_threads) == thread_count - 1
                assert len(db_posts) == post_count - 1
            case "nekobasu":
                # Test deleting ForumPosts
                # Count threads and posts before starting
                db_threads = session.exec(
                    select(ForumThread).where(ForumThread.user_id == user.id)
                ).all()
                thread_count = len(db_threads)
                db_posts = session.exec(
                    select(ForumPost).where(ForumPost.user_id == user.id)
                ).all()
                post_count = len(db_posts)

                headers = get_auth_header(
                    client, "nekobasu", "greendragonstuffy"
                )
                resp = client.delete(
                    f"/posts/{user.posts[0].id}",
                    headers=headers
                )
                db_user = session.get(ForumUser, user.id)
                db_threads = session.exec(
                    select(ForumThread).where(ForumThread.user_id == user.id)
                ).all()
                db_posts = session.exec(
                    select(ForumPost).where(ForumPost.user_id == user.id)
                ).all()

                assert resp.status_code == 204
                assert db_user is not None
                assert len(db_threads) == thread_count
                assert len(db_posts) == post_count - 1
            case _:
                """
                You really shouldn't be here, but here's
                a laconic explanation of this monstrosity:
                We need to check to make sure that the
                various delete functionalities work, and
                that they don't delete things that they
                shouldn't be deleting.
                """
