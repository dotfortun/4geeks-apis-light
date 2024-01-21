from concurrent.futures import thread
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
from api import db

from api.forum.models import (
    ForumPost,
    ForumThread,
    ForumUser,
    PostCreate,
    PostList,
    PostRead,
    PostUpdate,
)
from api.forum.routers.auth import get_current_user, get_password_hash
from api.db import get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@app.post(
    "/replyto/{thread_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=PostRead,
)
def reply_to_thread(
    thread_id: Annotated[int, Path(title="thread id")],
    post: PostCreate,
    current_user: Annotated[ForumUser, Depends(get_current_user)],
    request: Request,
    session: Session = Depends(get_session)
) -> None:
    db_post = ForumPost.model_validate({
        **post.model_dump(),
        "user_id": current_user.id,
        "thread_id": thread_id,
    })
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@app.get(
    "/",
    response_model=PostList,
)
def read_posts(
    request: Request,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    return {
        "posts": session.exec(
            select(ForumThread).offset(offset).limit(limit)
        ).all()
    }


@app.get(
    "/{post_id}",
    response_model=PostRead,
)
def get_single_post(
    post_id: Annotated[int, Path(title="thread id")],
    request: Request,
    session: Session = Depends(get_session)
):
    db_thread = session.exec(
        select(ForumPost).where(ForumPost.id == post_id)
    ).first()
    if not db_thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread #{post_id} doesn't exist."
        )
    return db_thread


@app.put(
    "/{post_id}",
    response_model=PostRead,
)
def update_post(
    post_id: Annotated[int, Path(title="thread id")],
    request: Request,
    post_data: PostUpdate,
    current_user: Annotated[ForumUser, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    db_post = session.exec(
        select(ForumPost).where(ForumPost.id == post_id)
    ).first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread #{post_id} doesn't exist."
        )
    if db_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You lack the permissions to edit this thread."
        )
    for k, v in post_data:
        if v is not None:
            setattr(db_post, k, v)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@app.delete(
    "/{post_id}",
)
def delete_post(
    request: Request,
    post_id: Annotated[int, Path(title="todo id")],
    current_user: Annotated[ForumUser, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    db_post = session.exec(
        select(ForumPost).where(ForumPost.id == post_id)
    ).first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread #{post_id} doesn't exist."
        )
    if db_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You lack the permissions to delete this thread."
        )
    session.delete(db_post)
    session.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
