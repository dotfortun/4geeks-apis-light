import os

from typing import List, Optional, Annotated

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

from .models import (
    TodoUser, TodoUserCreate, TodoUserRead, TodoUserReadWithItems,
    TodoItem, TodoItemCreate, TodoItemRead, TodoItemUpdate,
    TodoUserList, TodoItemList
)
from api.db import get_session


app = FastAPI(
    title="Todo API"
)

limiter = Limiter(key_func=get_remote_address)
# Limiter requires the request to be in the args for your routes!
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=TodoUserRead,
    tags=["User operations"],
)
@limiter.limit("15/minute")
def create_user(
    user: TodoUserCreate,
    request: Request,
    session: Session = Depends(get_session)
) -> None:
    user_exists = session.exec(select(TodoUser).where(
        TodoUser.name == user.name)).first()
    if not user_exists:
        db_user = TodoUser.model_validate(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User already exists."
    )


@app.delete(
    "/users/{user_name}",
    tags=["User operations"],
)
@limiter.limit("15/minute")
def delete_user(
    request: Request,
    user_name: Annotated[str, Path(title="username")],
    session: Session = Depends(get_session),
    tags=["User operations"],
):
    user = session.exec(select(TodoUser).where(
        TodoUser.name == user_name)
    ).first()
    if user:
        session.delete(user)
        session.commit()
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"User {user_name} doesn't exist."
    )


@app.get(
    "/users",
    response_model=TodoUserList,
    tags=["User operations"],
)
@limiter.limit("120/minute")
def get_users(
    request: Request,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    return {
        "users": session.exec(
            select(TodoUser).offset(offset).limit(limit)
        ).all()
    }


@app.get(
    "/users/{user_name}",
    response_model=TodoUserReadWithItems,
    tags=["User operations"],
)
@limiter.limit("120/minute")
def get_user(
    request: Request,
    user_name: Annotated[str, Path(title="username")],
    session: Session = Depends(get_session)
):
    user = session.exec(select(TodoUser).where(
        TodoUser.name == user_name)
    ).first()
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {user_name} doesn't exist."
    )


@app.post(
    "/todos",
    response_model=TodoItemCreate,
    tags=["Todo operations"],
)
@limiter.limit("60/minute")
def post_user_todo(
    request: Request,
    todo_item: TodoItemCreate,
    session: Session = Depends(get_session)
):
    user = session.get(TodoUser, todo_item.user_id)
    if user:
        db_todo = TodoItem.model_validate(todo_item)
        session.add(db_todo)
        session.commit()
        session.refresh(db_todo)
        return db_todo
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User #{todo_item.user_id} doesn't exist."
    )


@app.put(
    "/todos/{todo_id}",
    response_model=TodoItem,
    tags=["Todo operations"],
)
@limiter.limit("120/minute")
def put_user_todo(
    request: Request,
    todo_id: Annotated[int, Path(title="username")],
    todo_data: TodoItemUpdate,
    session: Session = Depends(get_session)
):
    todo = session.get(TodoItem, todo_id)
    if todo:
        for k, v in todo_data:
            todo[k] = v
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Todo #{todo_id} doesn't exist."
    )


@app.delete(
    "/todos/{todo_id}",
    tags=["Todo operations"],
)
@limiter.limit("120/minute")
def delete_user_todo(
    request: Request,
    todo_id: Annotated[int, Path(title="username")],
    session: Session = Depends(get_session)
):
    todo = session.get(TodoItem, todo_id)
    if todo:
        session.delete(todo)
        session.commit()
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Todo #{todo_id} doesn't exist."
    )
