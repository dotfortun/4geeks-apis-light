import os

from typing import List, Optional, Annotated

from fastapi import (
    APIRouter, Request, Response, HTTPException,
    Query, Depends, Path, status,
)
from fastapi.openapi.docs import get_swagger_ui_html

from passlib.context import CryptContext

from sqlmodel import (
    Session, select,
)

from api.forum.models import (
    ForumUser,
    PostRead,
    UserCreate, UserRead,
    UserReadDetails, UserUpdate, UserList
)
from api.forum.routers.auth import get_current_user, get_password_hash
from api.db import get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@app.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserReadDetails,
    summary="Create User.",
    description="Creates a new User.",
)
def create_user(
    user: UserCreate,
    request: Request,
    session: Session = Depends(get_session)
) -> None:
    user_exists = session.exec(select(ForumUser).where(
        ForumUser.username == user.username)).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists."
        )
    user.password = pwd_context.hash(user.password)
    db_user = ForumUser.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return UserReadDetails(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        posts=db_user.posts,
        threads=db_user.threads,
    )


@app.get(
    "/",
    response_model=UserList,
)
def read_users(
    request: Request,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    return {
        "users": session.exec(
            select(ForumUser).offset(offset).limit(limit)
        ).all()
    }


@app.get(
    "/{user_name}",
    response_model=UserReadDetails,
)
def read_user(
    user_name: Annotated[str, Path(title="username")],
    request: Request,
    session: Session = Depends(get_session)
):
    db_user = session.exec(
        select(ForumUser).where(ForumUser.username == user_name)
    ).first()
    return UserReadDetails(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        threads=db_user.threads,
        posts=db_user.posts,
    )


@app.put(
    "/",
    response_model=UserRead,
)
def update_user(
    request: Request,
    user_data: UserUpdate,
    current_user: Annotated[ForumUser, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User doesn't exist."
        )
    for k, v in user_data:
        if k == "password" and v is not None:
            setattr(current_user, k, get_password_hash(v))
            continue
        if v is not None:
            setattr(current_user, k, v)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@app.delete(
    "/{user_id}",
)
def delete_user(
    request: Request,
    user_id: Annotated[int, Path(title="todo id")],
    current_user: Annotated[ForumUser, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    user = session.get(ForumUser, user_id)
    if not all([user, current_user.id == user_id]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User #{user_id} doesn't exist."
        )
    session.delete(user)
    session.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
