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

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from sqlmodel import (
    Session, select
)

from api.{f_name}.models import (
    HelloWorld
)
from api.db import get_session

app = FastAPI(
    title="{name.title()} API"
)

limiter = Limiter(key_func=get_remote_address)
# Limiter requires the request to be in the args for your routes!
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get(
    "/hello",
    response_model=HelloWorld,
    tags=["User operations"],
)
@limiter.limit("15/minute")
def create_user(
    request: Request,
    session: Session = Depends(get_session)
) -> None:
    hello_world = HelloWorld(message="Hello, world!")
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
        unique=True,
    )


class HelloWorld(HelloWorldBase, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )

"""
    if f_name not in os.listdir("./api"):
        os.makedirs(f"./api/{f_name}")
        with open(f"./api/{f_name}/__init__.py", "w") as f:
            f.write(init)
        with open(f"./api/{f_name}/app.py", "w") as f:
            f.write(app)
        with open(f"./api/{f_name}/models.py", "w") as f:
            f.write(models)
        print(f"Module {name} created")
        return
    print(f"Module {name} already exists.")


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
mod_parser = subparsers.add_parser("create", aliases=["make"])
mod_parser.add_argument(
    "name",
    help="The name of the module you want to create.",
    type=str,
)
mod_parser.set_defaults(func=create_module)


if __name__ == "__main__":
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args.name)
