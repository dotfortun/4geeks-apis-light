import os

from sqlmodel import (
    Session, create_engine
)

engine = create_engine(
    os.getenv("DB_URL", "sqlite:///./playground.sqlite")
)


def get_session():
    with Session(engine) as session:
        yield session
