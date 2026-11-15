import os

os.environ["JWT_SECRET_KEY"] = "chave-local-apenas-para-testes-automatizados-123456789"
# O startup da app cria tabelas no engine padrão; apontá-lo para a memória impede
# que os testes criem ou alterem o arquivo eventech.db.
os.environ["DATABASE_URL"] = "sqlite://"

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base, get_db
from core.security import criar_hash, criar_token
from main import app
from models import Evento, Inscricao, Usuario

SENHA = "SenhaTeste@123"
ADMIN = "admin@teste.local"
PARTICIPANTE = "participante@teste.local"
OUTRO = "outro@teste.local"


@pytest.fixture
def sessao():
    """Banco SQLite em memória, isolado por teste. Nunca toca em eventech.db."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    with Session() as db:
        yield db
    engine.dispose()


@pytest.fixture
def ambiente(sessao):
    """Retorna (client, ids) com admin, dois participantes, 1 evento e 1 inscrição do `outro`."""
    db = sessao

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    admin = Usuario(nome="Admin", email=ADMIN, perfil="administrador", senha_hash=criar_hash(SENHA))
    participante = Usuario(nome="Participante", email=PARTICIPANTE, perfil="participante", senha_hash=criar_hash(SENHA))
    outro = Usuario(nome="Outro", email=OUTRO, perfil="participante", senha_hash=criar_hash(SENHA))
    db.add_all([admin, participante, outro])
    db.commit()
    evento = Evento(titulo="Evento teste", descricao="Teste", data_evento=date(2026, 12, 1), capacidade=20, carga_horaria=4)
    db.add(evento)
    db.commit()
    insc = Inscricao(id_usuario=outro.id_usuario, id_evento=evento.id_evento, status="Ativa")
    db.add(insc)
    db.commit()
    ids = {
        "admin": admin.id_usuario, "participante": participante.id_usuario, "outro": outro.id_usuario,
        "evento": evento.id_evento, "inscricao": insc.id_inscricao,
    }
    with TestClient(app) as client:
        yield client, ids
    app.dependency_overrides.clear()


@pytest.fixture
def auth():
    return lambda email: {"Authorization": "Bearer " + criar_token(email)}


@pytest.fixture
def evento_payload():
    return lambda **extra: {
        "titulo": "Novo evento", "descricao": "Descrição", "data_evento": "2026-12-02",
        "capacidade": 10, "carga_horaria": 3, **extra,
    }
