"""Configuração central da aplicação, lida exclusivamente de variáveis de ambiente.

Nenhum segredo fica no código. Em desenvolvimento, as variáveis podem vir de um
arquivo `.env` (ignorado pelo Git); em produção, são definidas no provedor.
"""
import os

from dotenv import load_dotenv

load_dotenv()

TAMANHO_MINIMO_SEGREDO = 32


def _normalizar_database_url(url: str) -> str:
    """Provedores como Heroku/Render entregam `postgres://`, que o SQLAlchemy 2 rejeita."""
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url


def obter_database_url() -> str:
    return _normalizar_database_url(os.environ.get("DATABASE_URL", "sqlite:///./eventech.db"))


def obter_segredo_jwt() -> str:
    chave = os.environ.get("JWT_SECRET_KEY")
    if not chave:
        raise RuntimeError("JWT_SECRET_KEY não configurada")
    if len(chave) < TAMANHO_MINIMO_SEGREDO:
        raise RuntimeError(
            f"JWT_SECRET_KEY deve ter pelo menos {TAMANHO_MINIMO_SEGREDO} caracteres"
        )
    return chave


def obter_expiracao_token_minutos() -> int:
    return int(os.environ.get("TOKEN_EXPIRE_MINUTES", "30"))


def obter_origens_cors() -> list[str]:
    bruto = os.environ.get("CORS_ORIGINS", "")
    return [origem.strip() for origem in bruto.split(",") if origem.strip()]
