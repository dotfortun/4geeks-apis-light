import argparse
import os
import re


def create_module(name: str):
    f_name = re.sub(r"[\s\<\>\:\"\/\\\|\?\*]", "_", name).lower()

    init = f"""from api.{f_name}.app import app
import api.{f_name}.models as models

__all__ = (
    'app',
    'models',
)

"""

    app = f"""from typing import List, Optional, Annotated

from fastapi import (
    FastAPI, Request, Response, HTTPException,
    Query, Depends, Path, status,
)
from fastapi.openapi.docs import get_swagger_ui_html

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from sqlmodel import (
    Session, select
)

from api.{f_name}.models import (
    HelloWorldRead
)
from api.db import get_session

app = FastAPI(
    title="{name.title()} API",
    description="An API that you should describe.",
    docs_url=None,
)

limiter = Limiter(key_func=get_remote_address)
# Limiter requires the request to be in the args for your routes!
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        title="4Geeks Playground - {name.title()} API",
        openapi_url="/{f_name}/openapi.json",
        swagger_favicon_url="/favicon.ico",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(
    "/hello/",
    response_model=HelloWorldRead,
    tags=["User operations"],
)
@limiter.limit("15/minute")
def hello_world(
    request: Request,
    session: Session = Depends(get_session)
) -> None:
    hello_world = HelloWorldRead(message="Hello, world!")
    return hello_world

"""

    models = """from typing import List, Optional

from sqlmodel import (
    SQLModel, Field, Relationship,
)
from pydantic import BaseModel

import sqlmodel


class HelloWorldBase(SQLModel):
    message: str = Field(
        index=True,
        unique=False,
    )


class HelloWorld(HelloWorldBase, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )

class HelloWorldRead(HelloWorldBase):
    pass

"""
    tests = f"""import pytest
from fastapi.testclient import TestClient
from sqlmodel import (
    Session, SQLModel, create_engine
)
from sqlalchemy.pool import StaticPool

from api.db import get_session
from api.{f_name}.app import app


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={'{"check_same_thread": False}'}, poolclass=StaticPool
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


def test_hello_world(client: TestClient):
    response = client.get(
        "/hello"
    )
    data = response.json()

    assert response.status_code == 200
    assert data["message"] == "Hello, world!"

"""
    if f_name not in os.listdir("./api"):
        os.makedirs(f"./api/{f_name}")
        with open(f"./api/{f_name}/__init__.py", "w") as f:
            f.write(init)
        with open(f"./api/{f_name}/app.py", "w") as f:
            f.write(app)
        with open(f"./api/{f_name}/models.py", "w") as f:
            f.write(models)
        with open(f"./api/{f_name}/test_app.py", "w") as f:
            f.write(tests)
        print(f"Module {name} created")
        return
    print(f"Module {name} already exists.")


def reset_db():
    confirm = input(
        "Are you sure you want to reset your db and migrations? y/N\n"
    )
    if confirm.lower() not in ["y", "yes"]:
        print("reset_db cancelled.")
        return
    for f_name in os.listdir("./migrations/versions"):
        if f_name != ".gitkeep":
            os.remove(f"./migrations/versions/{f_name}")
            pass
    db_name = os.getenv("DB_URL", "sqlite:///./playground.sqlite")
    if re.match(r"sqlite\:", db_name):
        db_name = re.sub(
            r"(^sqlite|/\.|[\:\/])",
            "",
            db_name
        )
        os.remove(f"./{db_name}")
    print("Database reset.")


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

mod_parser = subparsers.add_parser("create", aliases=["make"])
mod_parser.add_argument(
    "name",
    help="The name of the module you want to create.",
    type=str,
)
mod_parser.set_defaults(op="create_module", func=create_module)

reset_parser = subparsers.add_parser(
    "reset",
    aliases=["drop", "dropdb", "resetdb"]
)
reset_parser.set_defaults(op="reset_db", func=reset_db)


if __name__ == "__main__":
    args = parser.parse_args()

    match getattr(args, "op", None):
        case "create_module":
            args.func(args.name)
        case "reset_db":
            args.func()
        case _:
            print("How did you even get here?")
