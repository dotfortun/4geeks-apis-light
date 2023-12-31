from typing import List, Optional, Annotated

from fastapi import (
    FastAPI, Request, Response, HTTPException,
    Query, Depends, Path, status,
)

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from sqlmodel import (
    select
)

from api.contact.models import (
    ContactUser
)
from api.db import get_session

app = FastAPI(
    title="Contact List API"
)

limiter = Limiter(key_func=get_remote_address)
# Limiter requires the request to be in the args for your routes!
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# @app.post(
#     "/users",
#     status_code=status.HTTP_201_CREATED,
#     response_model=ContactUser,
#     tags=["User operations"],
# )
# @limiter.limit("15/minute")
# def create_user(
#     user: TodoUserCreate,
#     request: Request,
#     session: Session = Depends(get_session)
# ) -> None:
#     user_exists = session.exec(select(TodoUser).where(
#         TodoUser.name == user.name)).first()
#     if not user_exists:
#         db_user = TodoUser.model_validate(user)
#         session.add(db_user)
#         session.commit()
#         session.refresh(db_user)
#         return db_user
#     raise HTTPException(
#         status_code=status.HTTP_400_BAD_REQUEST,
#         detail="User already exists."
#     )
