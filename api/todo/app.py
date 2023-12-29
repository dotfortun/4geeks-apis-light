import os

from typing import List, Optional, Annotated

from fastapi import (
    FastAPI, Request, Response, HTTPException,
    Query, Depends, status,
)

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from sqlmodel import (
    Session, create_engine, select
)

from .models import (
    TodoUser, TodoUserCreate, TodoUserRead, TodoUserReadWithItems,
    TodoItem, TodoItemCreate, TodoItemRead, TodoItemUpdate,
    TodoUserList
)

app = FastAPI(
    title="Todo API"
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


engine = create_engine(
    os.getenv("DB_URL", "sqlite:///./playground.sqlite")
)


def get_session():
    with Session(engine) as session:
        yield session


@app.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=TodoUserRead
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
    "/users/{user_id: int}",
)
@limiter.limit("15/minute")
def delete_user(
    *,
    request: Request,
    user_id: int | None = None,
    session: Session = Depends(get_session)
):
    user = session.exec(select(TodoUser).where(
        TodoUser.name == user_id)
    ).first()
    if user:
        session.delete(user)
        session.commit()
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"User {user_id} doesn't exist."
    )


@app.get(
    "/users",
    response_model=TodoUserList
)
@limiter.limit("120/minute")
def get_users(
    request: Request,  # This is required for slowapi.
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    return {
        "users": session.exec(
            select(TodoUser).offset(offset).limit(limit)
        ).all()
    }
