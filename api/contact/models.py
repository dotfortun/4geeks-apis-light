import re

from typing import List, Optional

from sqlmodel import (
    SQLModel, Field, Relationship,
)
from pydantic import (
    BaseModel, ValidationInfo, field_validator
)

import sqlmodel


class AgendaBase(SQLModel):
    slug: str = Field(
        index=True,
        unique=True,
    )


class Agenda(AgendaBase, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    slug: str = Field(
        index=True,
        unique=True,
    )
    contacts: List["Contact"] = Relationship(back_populates="agenda")


class AgendaCreate(AgendaBase):
    pass


class AgendaRead(AgendaBase):
    id: int
    slug: str


class ContactBase(SQLModel):
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]


class Contact(ContactBase, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )

    user_id: int = Field(
        foreign_key="agenda.id"
    )
    agenda: Optional["Agenda"] = Relationship(back_populates="contacts")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str, info: ValidationInfo):
        if isinstance(v, str):
            is_valid = re.match(
                # This regex matches pretty many valid
                # phone numbers, and even more invalid ones.
                r"^\s*(?:\+?(\d{1,3}))?([-. (]*(\d{3})[-. )]*)?((\d{3})[-. ]*(\d{2,4})(?:[-.x ]*(\d+))?)\s*$",
                v
            )
            assert is_valid, f"{v} is not a valid phone number."
        return v


class ContactRead(ContactBase):
    id: int


class ContactCreate(ContactBase):
    name: str = Field(nullable=False)
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]


class ContactUpdate(ContactBase):
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]


# Models with relationships

class AgendaReadWithItems(AgendaBase):
    contacts: List["ContactRead"]


# Group models

class AgendaList(BaseModel):
    agendas: List["AgendaRead"]


class ContactList(BaseModel):
    contacts: List["ContactRead"]
