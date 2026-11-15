import os
os.environ["JWT_SECRET_KEY"] = "chave-local-apenas-para-testes-automatizados-123456789"
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from core.database import Base
from api.routes import get_db
from main import app
from models import Usuario, Evento, Inscricao
from core.security import criar_hash, criar_token
from datetime import date

@pytest.fixture
def ambiente():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    def override_db():
        with Session() as db:
            yield db
    app.dependency_overrides[get_db] = override_db
    with Session() as db:
        admin = Usuario(nome="Admin", email="admin@teste.local", perfil="administrador", senha_hash=criar_hash("SenhaTeste@123"))
        participante = Usuario(nome="Participante", email="participante@teste.local", perfil="participante", senha_hash=criar_hash("SenhaTeste@123"))
        outro = Usuario(nome="Outro", email="outro@teste.local", perfil="participante", senha_hash=criar_hash("SenhaTeste@123"))
        db.add_all([admin, participante, outro]); db.commit()
        ids = {"admin":admin.id_usuario,"participante":participante.id_usuario,"outro":outro.id_usuario}
        evento = Evento(titulo="Evento teste", descricao="Teste", data_evento=date(2026,12,1), capacidade=20, carga_horaria=4)
        db.add(evento); db.commit(); ids["evento"] = evento.id_evento
        insc = Inscricao(id_usuario=outro.id_usuario,id_evento=evento.id_evento,status="Ativa")
        db.add(insc);db.commit();ids["inscricao"] = insc.id_inscricao
    with TestClient(app) as client:
        yield client, ids
    app.dependency_overrides.clear()
    engine.dispose()

@pytest.fixture
def auth():
    return lambda email: {"Authorization": "Bearer " + criar_token(email)}
