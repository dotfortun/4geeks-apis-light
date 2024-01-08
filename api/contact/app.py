from typing import List, Optional, Annotated

from fastapi import (
    FastAPI, Request, Response, HTTPException,
    Query, Depends, Path, status,
)
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import ValidationError

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from sqlmodel import (
    Session, select
)

from api.contact.models import (
    Agenda, AgendaRead,
    Contact, ContactCreate, ContactRead, ContactUpdate,
    AgendaList, ContactList, AgendaReadWithItems,
)
from api.db import get_session

app = FastAPI(
    title="Contact List API",
    description="An API for storing contacts.",
    docs_url=None,
)

limiter = Limiter(key_func=get_remote_address)
# Limiter requires the request to be in the args for your routes!
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return await request_validation_exception_handler(request, exc)


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        title="4Geeks Playground - Contact List API",
        openapi_url="/contact/openapi.json",
        swagger_favicon_url="/favicon.ico",
        # swagger_css_url="/static/swagger-ui.css",
    )


@app.get(
    "/agendas",
    response_model=AgendaList,
    tags=["Agenda operations"],
    summary="Get All Agendas.",
)
@limiter.limit("120/minute")
def get_agendas(
    request: Request,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    return {
        "agendas": session.exec(
            select(Agenda).offset(offset).limit(limit)
        ).all()
    }


@app.get(
    "/agendas/{slug}",
    response_model=AgendaReadWithItems,
    tags=["Agenda operations"],
)
@limiter.limit("120/minute")
def get_agenda(
    request: Request,
    slug: Annotated[str, Path(title="slug")],
    session: Session = Depends(get_session)
):
    agenda = session.exec(select(Agenda).where(
        Agenda.slug == slug)
    ).first()
    if agenda:
        return agenda
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"""Agenda "{slug}" doesn't exist."""
    )


@app.post(
    "/agendas/{slug}",
    status_code=status.HTTP_201_CREATED,
    response_model=AgendaRead,
    tags=["Agenda operations"],
)
@limiter.limit("15/minute")
def create_agenda(
    request: Request,
    slug: Annotated[str, Path(title="slug")],
    session: Session = Depends(get_session)
) -> None:
    user_exists = session.exec(select(Agenda).where(
        Agenda.slug == slug)).first()
    if not user_exists:
        db_user = Agenda(slug=slug)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"""Agenda "{slug}" already exists."""
    )


@app.delete(
    "/agendas/{slug}",
    tags=["Agenda operations"],
)
@limiter.limit("15/minute")
def delete_agenda(
    request: Request,
    slug: Annotated[str, Path(title="slug")],
    session: Session = Depends(get_session),
    tags=["Agenda operations"],
):
    user = session.exec(select(Agenda).where(
        Agenda.slug == slug)
    ).first()
    if user:
        session.delete(user)
        session.commit()
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"""Agenda "{slug}" doesn't exist."""
    )


@app.get(
    "/agendas/{slug}/contacts",
    response_model=ContactList,
    tags=["Contact operations"],
)
@limiter.limit("60/minute")
def get_agenda_contacts(
    request: Request,
    slug: Annotated[str, Path(title="slug")],
    session: Session = Depends(get_session)
):
    agenda = session.exec(select(Agenda).where(
        Agenda.slug == slug)
    ).first()
    if agenda:
        return ContactList(
            contacts=agenda.contacts
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"""Agenda "{slug}" doesn't exist."""
    )


@app.post(
    "/agendas/{slug}/contacts",
    response_model=ContactRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Contact operations"],
)
@limiter.limit("60/minute")
def post_agenda_contact(
    request: Request,
    slug: Annotated[str, Path(title="slug")],
    contact: ContactCreate,
    session: Session = Depends(get_session)
):
    agenda = session.exec(select(Agenda).where(
        Agenda.slug == slug)
    ).first()
    if agenda:
        db_contact = Contact.model_validate({
            "name": contact.name,
            "phone": contact.phone or "",
            "email": contact.email or "",
            "address": contact.address or "",
            "agenda_id": agenda.id,
        })
        session.add(db_contact)
        session.commit()
        session.refresh(db_contact)
        return db_contact
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"""Agenda "{slug}" doesn't exist."""
    )


@app.put(
    "/agendas/{slug}/contacts/{contact_id}",
    response_model=ContactRead,
    tags=["Contact operations"],
)
@limiter.limit("60/minute")
def get_agenda_contacts(
    request: Request,
    slug: Annotated[str, Path(title="slug")],
    contact_id: Annotated[int, Path(title="contact id")],
    contact: ContactUpdate,
    session: Session = Depends(get_session)
):
    db_contact = session.get(
        Contact,
        contact_id
    )
    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"""Contact #{contact.id} doesn't exist."""
        )
    if slug != db_contact.agenda.slug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"""Contact #{contact.id} doesn't exist in Agenda "{slug}"."""
        )
    for k, v in contact:
        if v is not None:
            setattr(db_contact, k, v)
    session.add(db_contact)
    session.commit()
    session.refresh(db_contact)
    return db_contact


@app.delete(
    "/agendas/{slug}/contacts/{contact_id}",
    tags=["Contact operations"],
)
@limiter.limit("120/minute")
def delete_agenda_contact(
    request: Request,
    slug: Annotated[str, Path(title="slug")],
    contact_id: Annotated[int, Path(title="contact id")],
    session: Session = Depends(get_session)
):
    db_contact = session.get(Contact, contact_id)
    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"""Contact #{db_contact.id} doesn't exist."""
        )
    if db_contact.agenda.slug != slug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"""Contact #{db_contact.id} doesn't exist in Agenda "{slug}"."""
        )
    session.delete(db_contact)
    session.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
