import os

from typing import List, Optional, Annotated

from fastapi import (
    FastAPI, Request, Response, HTTPException,
    Query, Depends, Path, status,
)
from fastapi.openapi.docs import get_swagger_ui_html

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from sqlmodel import (
    Session, select,
)

from api.forum.models import (
    ForumUser,
    UserCreate, UserRead, UserUpdate, UserList
)
from api.forum.routers.auth import app as auth
from api.forum.routers.users import app as users
from api.db import get_session

app = FastAPI(
    title="Forum API",
    description="An API that you should describe.",
    docs_url=None,
)

limiter = Limiter(key_func=get_remote_address)
# Limiter requires the request to be in the args for your routes!
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routers
app.include_router(auth)
app.include_router(users)


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        title="4Geeks Playground - Forum API",
        openapi_url="/forum/openapi.json",
        swagger_favicon_url="/favicon.ico",
    )
