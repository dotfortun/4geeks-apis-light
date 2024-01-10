import json
from typing import List, Optional, Annotated

from fastapi import (
    FastAPI, Request, Response, HTTPException,
    Query, Depends, Path, status,
)
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from sqlmodel import (
    Session, select
)

from api.sound.models import (
    Song, Songs,
    FX, FXs,
    SoundData,
)
from api.db import get_session

app = FastAPI(
    title="Sound API",
    description="An API serving sound files.",
    docs_url=None,
)

limiter = Limiter(key_func=get_remote_address)
# Limiter requires the request to be in the args for your routes!
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.mount("/files", StaticFiles(directory="api/sound/files"), name="files")

data = {
    "sound_effects": None,
    "songs": None,
}

with (
    open("api/sound/data/fx.json", "rt") as fx_file,
    open("api/sound/data/songs.json", "rt") as song_file
):
    data["sound_effects"] = json.load(fx_file)
    data["songs"] = json.load(song_file)


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        title="4Geeks Playground - Sound API",
        openapi_url="/sound/openapi.json",
        swagger_favicon_url="/favicon.ico",
    )


@app.get(
    "/effects",
    response_model=FXs
)
def get_all_fx():
    return {
        "sound_effects": data["sound_effects"]
    }


@app.get(
    "/songs",
    response_model=Songs
)
def get_all_music():
    return {
        "songs": data["songs"]
    }


@app.get(
    "/all",
    response_model=SoundData
)
@limiter.limit("15/minute")
def get_all_data(
    request: Request,
    session: Session = Depends(get_session)
) -> None:
    return data
