import pytest

from core import config


def test_postgres_url_e_normalizada(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@host:5432/db")
    assert config.obter_database_url() == "postgresql://u:p@host:5432/db"


def test_database_url_padrao_e_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert config.obter_database_url().startswith("sqlite:///")


def test_segredo_ausente_falha(monkeypatch):
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="não configurada"):
        config.obter_segredo_jwt()


def test_segredo_curto_falha(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "curta")
    with pytest.raises(RuntimeError, match="pelo menos"):
        config.obter_segredo_jwt()


def test_origens_cors_sao_separadas_por_virgula(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://a.com, https://b.com ,")
    assert config.obter_origens_cors() == ["https://a.com", "https://b.com"]
