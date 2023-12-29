from typing import List

from sqlalchemy import (
    Boolean, Column, ForeignKey, Integer, String,
)
from sqlalchemy.orm import (
    relationship, Mapped,
)

from db.database import Base


class TodoUser(Base):
    __tablename__ = "todo_user"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)

    todos: Mapped[List["TodoItem"]] = relationship(
        "TodoItem",
        back_populates="user"
    )


class TodoItem(Base):
    __tablename__ = "todo_item"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, index=True, nullable=False)
    is_done = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("todo_user.id"), nullable=False)

    user: Mapped["TodoUser"] = relationship(
        "TodoUser",
        back_populates="todos"
    )
