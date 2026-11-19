from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import obter_database_url

DATABASE_URL = obter_database_url()

# `check_same_thread` é uma restrição específica do SQLite.
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args, pool_pre_ping=True)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _ativar_chaves_estrangeiras(conexao, _):
        # SQLite ignora FKs por padrão; sem isto, registros órfãos passariam despercebidos.
        conexao.execute("PRAGMA foreign_keys=ON")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependência FastAPI: uma sessão por requisição, sempre fechada ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def criar_tabelas() -> None:
    """Cria as tabelas ausentes. Chamado no startup da aplicação, não no import."""
    import models  # noqa: F401  (registra as entidades no metadata)

    Base.metadata.create_all(bind=engine)
