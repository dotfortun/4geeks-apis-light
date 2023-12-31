from typing import List, Optional

from sqlmodel import (
    SQLModel, Field, Relationship,
)
from pydantic import BaseModel

import sqlmodel


class ContactUserBase(SQLModel):
    slug: str = Field(
        index=True,
        unique=True,
    )


class ContactUser(ContactUserBase, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
