from typing import List, Optional

from sqlmodel import (
    SQLModel, Field, Relationship,
)
from pydantic import BaseModel


class TodoUserBase(SQLModel):
    name: str = Field(
        index=True,
        unique=True,
    )


class TodoUser(TodoUserBase, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    todos: List["TodoItem"] = Relationship(back_populates="user")


class TodoUserCreate(TodoUserBase):
    name: str


class TodoUserRead(TodoUserBase):
    id: int
    name: str


class TodoItemBase(SQLModel):
    label: str
    is_done: bool = Field(default=False)


class TodoItem(TodoItemBase, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )
    label: str
    user_id: int = Field(
        foreign_key="todouser.id"
    )
    user: Optional["TodoUser"] = Relationship(back_populates="todos")


class TodoItemCreate(TodoItemBase):
    pass


class TodoItemRead(TodoItemBase):
    id: int
    label: str
    is_done: bool


class TodoItemUpdate(TodoItemBase):
    label: Optional[str]
    is_done: Optional[bool]


# Models with relationships

class TodoUserReadWithItems(TodoUserBase):
    todos: List["TodoItemRead"]


# Group models

class TodoUserList(BaseModel):
    users: List[TodoUserRead]


class TodoItemList(BaseModel):
    todos: List[TodoItem]
