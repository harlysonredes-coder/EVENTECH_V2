from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from core.config import obter_expiracao_token_minutos, obter_segredo_jwt

password_hash = PasswordHash.recommended()

ALGORITHM = "HS256"


def criar_hash(senha: str) -> str:
    return password_hash.hash(senha)


def verificar_senha(senha: str, hash_salvo: str | None) -> bool:
    """Retorna False (em vez de lançar erro) para usuários sem senha cadastrada."""
    if not hash_salvo:
        return False
    return password_hash.verify(senha, hash_salvo)


def criar_token(email: str) -> str:
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=obter_expiracao_token_minutos())
    return jwt.encode({"sub": email, "exp": expiracao}, obter_segredo_jwt(), algorithm=ALGORITHM)


def validar_token(token: str) -> str:
    dados = jwt.decode(token, obter_segredo_jwt(), algorithms=[ALGORITHM])
    return dados["sub"]
