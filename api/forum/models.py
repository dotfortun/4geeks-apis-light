from typing import List, Optional

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

