import os

from datetime import timedelta, datetime, timezone

from typing import List, Optional, Annotated

from fastapi import (
    APIRouter, Request, Response, HTTPException,
    Query, Depends, Path, status,
)
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import (
    OAuth2PasswordBearer, OAuth2PasswordRequestForm
)

from jose import JWTError, jwt

from passlib.context import CryptContext

from sqlmodel import (
    Session, select,
)

from api.forum.models import (
    ForumUser, UserRead,
    Login, Token, TokenData
)
from api.db import get_session

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "Some valid secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = session.exec(select(ForumUser).where(
        ForumUser.username == token_data.username)).first()
    if user is None:
        raise credentials_exception
    return user


app = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@app.post(
    "/token",
    status_code=status.HTTP_201_CREATED,
    response_model=Token,
    summary="Get user credentials.",
    description="Gets token for future access.",
)
def login(
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    session: Session = Depends(get_session)
) -> None:
    user = session.exec(select(ForumUser).where(
        ForumUser.username == login_data.username)).first()

    if not all([user, verify_password(login_data.password, user.password)]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return Token(
        access_token=access_token,
        token_type="bearer"
    )
