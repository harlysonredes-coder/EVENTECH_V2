"""Dependências de autenticação e autorização reutilizadas pelas rotas."""
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.exceptions import AcessoNegado, NaoAutenticado
from core.security import validar_token
from services import usuarios

seguranca = HTTPBearer(
    scheme_name="BearerAuth",
    bearerFormat="JWT",
    description="Token JWT obtido em `POST /login`. Informe apenas o token (sem o prefixo `Bearer`).",
    auto_error=False,
)


def exigir_autenticacao(credenciais: HTTPAuthorizationCredentials | None = Depends(seguranca)) -> str:
    if credenciais is None:
        raise NaoAutenticado()
    try:
        return validar_token(credenciais.credentials)
    except Exception:
        raise NaoAutenticado("Token inválido ou expirado")


def usuario_atual(email: str = Depends(exigir_autenticacao), db: Session = Depends(get_db)):
    usuario = usuarios.buscar_por_email(db, email)
    if usuario is None:
        raise NaoAutenticado("Usuário do token não existe mais")
    return usuario


def exigir_administrador(atual=Depends(usuario_atual)):
    if not usuarios.eh_admin(atual):
        raise AcessoNegado("Acesso permitido apenas para administradores")
    return atual
