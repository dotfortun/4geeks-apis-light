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

from api.forum.routers.auth import app as auth
from api.forum.routers.users import app as users
from api.forum.routers.threads import app as threads
from api.forum.routers.posts import app as posts

app = FastAPI(
    title="Forum API",
    description="A more advanced API with Oauth2.",
    docs_url=None,
)

limiter = Limiter(key_func=get_remote_address)
# Limiter requires the request to be in the args for your routes!
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routers
app.include_router(auth)
app.include_router(users)
app.include_router(threads)
app.include_router(posts)


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        title="4Geeks Playground - Forum API",
        openapi_url="/forum/openapi.json",
        swagger_favicon_url="/favicon.ico",
    )


@app.get("/scalar", include_in_schema=False)
async def scalar_ui_html():
    return Response(
        content=f"""
<!doctype html>
<html>
  <head>
    <title>4Geeks Playground - Forum API</title>
    <meta charset="utf-8" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1" />
  </head>
  <body style="margin: 0">
    <script
      id="api-reference"
      data-url="/forum/openapi.json"
    ></script>
    <!-- You can also set a full configuration object like this -->
    <!-- easier for nested objects -->
    <script>
      var configuration = {'''{
        theme: 'deepSpace',
      }'''}

      var apiReference = document.getElementById('api-reference')
      apiReference.dataset.configuration = JSON.stringify(configuration)
    </script>
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
  </body>
</html>
"""
    )
