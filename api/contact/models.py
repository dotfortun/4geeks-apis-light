from typing import List, Optional, Union

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
    contacts: List["Contact"] = Relationship(
        back_populates="agenda",
        sa_relationship_kwargs={"cascade": "delete"}
    )


class AgendaRead(AgendaBase):
    id: int
    slug: str


class ContactBase(SQLModel):
    name: str
    phone: Optional[str] = Field(default="")
    email: Optional[str] = Field(default="")
    address: Optional[str] = Field(default="")


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
    name: str
    phone: str
    email: str
    address: str


class ContactCreate(ContactBase):
    name: str = Field(nullable=False)
    phone: Optional[str] = Field(default="")
    email: Optional[str] = Field(default="")
    address: Optional[str] = Field(default="")


class ContactUpdate(ContactBase):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


# Models with relationships

class AgendaReadWithItems(AgendaBase):
    contacts: List["ContactRead"]


# Group models

class AgendaList(BaseModel):
    agendas: List["AgendaRead"]


class ContactList(BaseModel):
    contacts: List["ContactRead"]
