import pytest
from fastapi.testclient import TestClient
from sqlmodel import (
    Session, SQLModel, create_engine, select
)
from sqlalchemy.pool import StaticPool

from api.db import get_session
from api.contact.app import app
from api.contact.models import (
    Agenda, Contact
)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_agenda(client: TestClient):
    response = client.post(
        "/agendas/grizelle"
    )
    data = response.json()

    assert response.status_code == 201
    assert data["slug"] == "grizelle"
    assert data["id"] is not None


def test_get_agendas(session: Session, client: TestClient):
    agendas = [
        Agenda(slug="grizelle"),
        Agenda(slug="sombra"),
    ]
    for agenda in agendas:
        session.add(agenda)
    session.commit()

    resp = client.get(
        "/agendas"
    )
    data = resp.json()

    assert resp.status_code == 200
    assert isinstance(data["agendas"], list)
    assert len(data["agendas"]) == 2
    assert "grizelle" in [agenda["slug"] for agenda in data["agendas"]]
    assert "sombra" in [agenda["slug"] for agenda in data["agendas"]]


def test_post_contacts(session: Session, client: TestClient):
    sombra = Agenda(slug="sombra")
    session.add(sombra)
    session.commit()

    resp = client.post(
        "/agendas/sombra/contacts",
        json={
            "name": "Grizelle",
            "phone": "1 (603) 555-1234",
            "email": "grizelle@catemail.com",
            "address": "123 Nonesuch Pl, Catington CA"
        }
    )
    data = resp.json()

    sombra = session.exec(select(Agenda).where(
        Agenda.slug == "sombra")
    ).first()

    assert resp.status_code == 201
    assert len(sombra.contacts) == 1
    assert data["name"] == "Grizelle"
    assert data["phone"] == "1 (603) 555-1234"
    assert data["email"] == "grizelle@catemail.com"
    assert data["address"] == "123 Nonesuch Pl, Catington CA"

    resp = client.post(
        "/agendas/sombra/contacts",
        json={
            "name": "Nekobasu"
        }
    )
    data = resp.json()

    sombra = session.exec(select(Agenda).where(
        Agenda.slug == "sombra")
    ).first()

    assert resp.status_code == 201
    assert len(sombra.contacts) == 2


def test_put_contact(session: Session, client: TestClient):
    sombra = Agenda(slug="sombra")
    session.add(sombra)
    session.commit()

    grizelle = Contact(
        name="Oops, no data!",
        phone="Oops, no data!",
        email="Oops, no data!",
        address="Oops, no data!",
        agenda_id=sombra.id
    )
    session.add(grizelle)
    session.commit()
    session.refresh(grizelle)

    resp = client.put(
        f"/agendas/sombra/contacts/{grizelle.id}",
        json={
            "name": "Grizzle",
            "phone": "1 (603) 555-1234",
            "email": "grizelle@catemail.com",
            "address": "123 Nonesuch Pl, Catington CA"
        }
    )
    data = resp.json()

    sombra = session.exec(select(Agenda).where(
        Agenda.slug == "sombra")
    ).first()

    assert resp.status_code == 200
    assert len(sombra.contacts) == 1
    assert data["name"] == "Grizzle"
    assert data["phone"] == "1 (603) 555-1234"
    assert data["email"] == "grizelle@catemail.com"
    assert data["address"] == "123 Nonesuch Pl, Catington CA"

    resp = client.put(
        f"/agendas/sombra/contacts/{grizelle.id}",
        json={
            "name": "Grizelle"
        }
    )
    data = resp.json()

    sombra = session.exec(select(Agenda).where(
        Agenda.slug == "sombra")
    ).first()

    assert resp.status_code == 200
    assert len(sombra.contacts) == 1
    assert data["name"] == "Grizelle"
    assert data["phone"] == "1 (603) 555-1234"
    assert data["email"] == "grizelle@catemail.com"
    assert data["address"] == "123 Nonesuch Pl, Catington CA"


def test_delete_contacts(session: Session, client: TestClient):
    sombra = Agenda(slug="sombra")
    session.add(sombra)
    session.commit()

    grizelle = Contact(
        name="Oops, no data!",
        phone="Oops, no data!",
        email="Oops, no data!",
        address="Oops, no data!",
        agenda_id=sombra.id
    )
    session.add(grizelle)
    session.commit()
    session.refresh(grizelle)

    resp = client.delete(
        f"/agendas/sombra/contacts/{grizelle.id}",
    )

    sombra = session.exec(select(Agenda).where(
        Agenda.slug == "sombra")
    ).first()

    assert resp.status_code == 204
    assert len(sombra.contacts) == 0


def test_delete_agenda(session: Session, client: TestClient):
    sombra = Agenda(slug="sombra")
    session.add(sombra)
    session.commit()
    session.refresh(sombra)

    session.add(Agenda(slug="test"))
    session.commit()

    grizelle = Contact(
        name="Oops, no data!",
        phone="Oops, no data!",
        email="Oops, no data!",
        address="Oops, no data!",
        agenda_id=sombra.id
    )
    session.add(grizelle)
    session.commit()
    session.refresh(grizelle)

    resp = client.delete(
        f"/agendas/sombra",
    )

    sombra = session.get(Agenda, sombra.id)
    grizelle = session.get(Contact, grizelle.id)
    agendas = session.exec(select(Agenda)).all()

    assert resp.status_code == 204
    assert sombra is None
    assert grizelle is None
    assert len(agendas) == 1
