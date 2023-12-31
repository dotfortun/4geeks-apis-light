import re

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import api

template = None
with open("./static/index.html", "r") as f:
    template = f.read()


app = FastAPI(
    title="4Geeks Playground",
)

for mod in api.__all__:
    if re.search("pycache", mod.__name__):
        continue
    name = re.sub("api\.", "", mod.__name__)
    app.mount(f"""/{name}""", getattr(mod, "app"), name)


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/", include_in_schema=False)
async def app_root(request: Request):
    routes = ""
    for mod in api.__all__:
        name = re.sub("api\.", "", mod.__name__)
        routes += f"""<li><a href="/{name}/docs">{name.title()}</a></li>"""
    return HTMLResponse(
        content=re.sub(r"{{ content }}", f"<ul>{routes}</ul>", template)
    )


@app.get("/ratelimit")
@limiter.limit("5/minute")
async def rate_limited(request: Request):
    return {
        "message": "This API endpoint is rate limited."
    }
