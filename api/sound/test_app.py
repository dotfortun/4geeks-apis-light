import pytest
from fastapi.testclient import TestClient
from sqlmodel import (
    Session, SQLModel, create_engine
)
from sqlalchemy.pool import StaticPool

from api.db import get_session
from api.sound.app import app


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


# def test_hello_world(client: TestClient):
#     response = client.get(
#         "/hello"
#     )
#     data = response.json()

#     assert response.status_code == 200
#     assert data["message"] == "Hello, world!"
