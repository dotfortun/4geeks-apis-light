from typing import List, Optional

from sqlmodel import (
    SQLModel, Field, Relationship,
)
from pydantic import (
    BaseModel
)


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

    agenda_id: int = Field(
        foreign_key="agenda.id"
    )
    agenda: Optional["Agenda"] = Relationship(back_populates="contacts")


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
