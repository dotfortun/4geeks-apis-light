import re

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)

for mod in api.__all__:
    if re.search("pycache", mod.__name__):
        continue
    name = re.sub("api\.", "", mod.__name__)
    subapp: FastAPI = getattr(mod, "app")
    subapp.contact = {
        "email": "info@4geeks.com"
    }
    app.mount(f"""/{name}""", subapp, name)

app.mount("/static", StaticFiles(directory="static"), name="static")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/", include_in_schema=False)
async def app_root(request: Request):
    routes = ""
    for mod in api.__all__:
        if re.search("pycache", mod.__name__):
            continue
        name = re.sub("api\.", "", mod.__name__)
        mod_app = getattr(mod, "app", dict())
        routes += f"""<li><a href="/{name}/docs">{getattr(mod_app, "title", "")}</a> - {getattr(mod_app, "description", "")}</li>"""
    return HTMLResponse(
        content=re.sub(
            r"{{ content }}",
            f"{routes}",
            template
        )
    )


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("static/4geeks.ico")
