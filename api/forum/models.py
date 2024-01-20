from datetime import datetime
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
    posts: Optional["ForumPost"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "delete"}
    )
    threads: Optional["ForumThread"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "delete"}
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

class ThreadBase(SQLModel):
    title: str
    content: str


class ForumThread(ThreadBase, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    created: datetime = Field(
        default=datetime.utcnow(),
        nullable=False
    )
    updated: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    title: str
    content: str
    user_id: int = Field(
        foreign_key="forumuser.id"
    )
    user: Optional["ForumUser"] = Relationship(back_populates="threads")
    posts: Optional["ForumPost"] = Relationship(
        back_populates="thread",
        sa_relationship_kwargs={"cascade": "delete"}
    )


class ThreadCreate(ThreadBase):
    pass


class ThreadRead(ThreadBase):
    id: int
    user: UserRead
    posts: Optional[List["PostRead"]] = None


class ThreadUpdate(ThreadBase):
    title: Optional[str] = None
    content: Optional[str] = None


# endregion: Threads


# region: Posts

class PostBase(SQLModel):
    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )
    content: str


class ForumPost(PostBase, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )
    content: str
    thread_id: int = Field(
        foreign_key="forumthread.id"
    )
    thread: Optional["ForumThread"] = Relationship(
        back_populates="posts"
    )
    user_id: int = Field(
        foreign_key="forumuser.id"
    )
    user: Optional["ForumUser"] = Relationship(
        back_populates="posts"
    )
    created: datetime = Field(
        default=datetime.utcnow(),
        nullable=False
    )
    updated: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )


class PostCreate(PostBase):
    pass


class PostRead(PostBase):
    id: int


class PostsRead(PostBase):
    id: int


class PostUpdate(PostBase):
    pass


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
    users: List[UserRead]


class ThreadList(BaseModel):
    threads: List[ThreadRead]


class PostList(BaseModel):
    posts: List[PostsRead]


# endregion: List Models


# region: Models with annoying relationships


class UserReadDetails(UserBase):
    posts: Optional["PostRead"]
    threads: Optional["ThreadRead"]


class UserReadDetails(UserBase):
    posts: List["PostRead"]
    threads: List["ThreadRead"]


#  endregion: Models with annoying relationships
