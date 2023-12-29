from typing import List, Optional

from sqlmodel import (
    SQLModel, Field, Relationship,
)


class TodoUserBase(SQLModel):
    name: str = Field(index=True)


class TodoUser(TodoUserBase, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )
    todos: List["TodoItem"] = Relationship(back_populates="user")


class TodoItemBase(SQLModel):
    label: str = Field(index=True)
    is_done: bool = Field(default=False)


class TodoItem(TodoItemBase, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )
    user: Optional["TodoUser"] = Relationship(back_populates="todos")
