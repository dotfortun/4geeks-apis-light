from typing import Dict, List, Optional

from sqlmodel import (
    SQLModel, Field, Relationship,
)
from pydantic import BaseModel


class Sound(BaseModel):
    id: int
    name: str
    url: str


class FX(Sound):
    category: str


class Song(Sound):
    game: str


class FXs(BaseModel):
    sound_effects: List[FX]


class Songs(BaseModel):
    songs: List[Song]


class SoundData(BaseModel):
    sound_effects: List[FX]
    songs: List[Song]
