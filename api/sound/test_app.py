import pytest
import json
import os

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


def test_files_exist(client: TestClient):
    data = {
        "sound_effects": None,
        "songs": None,
    }

    with (
        open("api/sound/data/fx.json", "rt") as fx_file,
        open("api/sound/data/songs.json", "rt") as song_file
    ):
        data["sound_effects"] = json.load(fx_file)
        data["songs"] = json.load(song_file)

    for song in data["sound_effects"]:
        assert os.path.isfile(f"""api/{song["url"]}""")

    for song in data["songs"]:
        assert os.path.isfile(f"""api/{song["url"]}""")
