from typing import List, Optional

from sqlmodel import (
    SQLModel, Field, Relationship,
)
from pydantic import BaseModel

import sqlmodel


# region: Users

class UserBase(SQLModel):
    username: str = Field(
        index=True,
        unique=True,
        nullable=False
    )
    email: str = Field(
        index=True,
        unique=True,
        nullable=False
    )


class ForumUser(UserBase, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    password: str = Field(
        nullable=False
    )


class UserCreate(UserBase):
    username: str
    email: str
    password: str


class UserRead(UserBase):
    pass


class UserUpdate(UserBase):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

# endregion: Users


# region: Threads

# endregion: Threads


# region: Posts


# endregion: Posts


# region: Auth

class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# endregion: Auth


# region: List Models

class UserList(BaseModel):
    users: List[ForumUser]

# endregion: List Models
