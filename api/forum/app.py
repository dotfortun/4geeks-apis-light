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
    Session, select
)

from api.forum.models import (
    HelloWorldRead
)
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


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        title="4Geeks Playground - Forum API",
        openapi_url="/forum/openapi.json",
        swagger_favicon_url="/favicon.ico",
    )


@app.get(
    "/hello/",
    response_model=HelloWorldRead,
    tags=["User operations"],
)
@limiter.limit("15/minute")
def hello_world(
    request: Request,
    session: Session = Depends(get_session)
) -> None:
    hello_world = HelloWorldRead(message="Hello, world!")
    return hello_world

