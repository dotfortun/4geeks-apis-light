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
    ForumThread,
    ForumUser,
    ThreadCreate,
    ThreadList,
    ThreadRead,
    ThreadReadDetails,
    ThreadUpdate,
)
from api.forum.routers.auth import get_current_user, get_password_hash
from api.db import get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = APIRouter(
    prefix="/threads",
    tags=["Threads"],
)


@app.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ThreadRead,
)
def create_thread(
    thread: ThreadCreate,
    current_user: Annotated[ForumUser, Depends(get_current_user)],
    request: Request,
    session: Session = Depends(get_session)
) -> None:
    db_thread = ForumThread.model_validate({
        **thread.model_dump(),
        "user_id": current_user.id,
    })
    session.add(db_thread)
    session.commit()
    session.refresh(db_thread)
    return db_thread


@app.get(
    "/",
    response_model=ThreadList,
)
def read_threads(
    request: Request,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    return {
        "threads": session.exec(
            select(ForumThread).offset(offset).limit(limit)
        ).all()
    }


@app.get(
    "/{thread_id}",
    response_model=ThreadRead,
)
def read_thread(
    thread_id: Annotated[int, Path(title="thread id")],
    request: Request,
    session: Session = Depends(get_session)
):
    db_thread = session.exec(
        select(ForumThread).where(ForumThread.id == thread_id)
    ).first()
    if not db_thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread #{thread_id} doesn't exist."
        )
    return db_thread


@app.put(
    "/{thread_id}",
    response_model=ThreadRead,
)
def update_thread(
    thread_id: Annotated[int, Path(title="thread id")],
    request: Request,
    thread_data: ThreadUpdate,
    current_user: Annotated[ForumUser, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    db_thread = session.exec(
        select(ForumThread).where(ForumThread.id == thread_id)
    ).first()
    if not db_thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread #{thread_id} doesn't exist."
        )
    if db_thread.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You lack the permissions to edit this thread."
        )
    for k, v in thread_data:
        if v is not None:
            setattr(db_thread, k, v)
    session.add(db_thread)
    session.commit()
    session.refresh(db_thread)
    return db_thread


@app.delete(
    "/{thread_id}",
)
def delete_thread(
    request: Request,
    thread_id: Annotated[int, Path(title="todo id")],
    current_user: Annotated[ForumUser, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    db_thread = session.exec(
        select(ForumThread).where(ForumThread.id == thread_id)
    ).first()
    if not db_thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread #{thread_id} doesn't exist."
        )
    if db_thread.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You lack the permissions to delete this thread."
        )
    session.delete(db_thread)
    session.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
