import re

from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import api

app = FastAPI(
    title="4Geeks Playground",
)

for mod in api.__all__:
    name = re.sub("api\.", "", mod.__name__)
    app.mount(f"""/{name}""", getattr(mod, "app"))


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
async def root(request: Request):
    return {
        "message": ""
    }


@app.get("/ratelimit")
@limiter.limit("5/minute")
async def rate_limited(request: Request):
    return {
        "message": "This API endpoint is rate limited."
    }
