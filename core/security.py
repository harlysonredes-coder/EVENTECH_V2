
import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from dotenv import load_dotenv
load_dotenv()
password_hash = PasswordHash.recommended()

ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30


def criar_hash(senha: str) -> str:
    return password_hash.hash(senha)


def verificar_senha(senha: str, hash_salvo: str) -> bool:
    return password_hash.verify(senha, hash_salvo)


def criar_token(email: str) -> str:
    chave = os.environ.get("JWT_SECRET_KEY")

    if not chave:
        raise RuntimeError("JWT_SECRET_KEY nao configurada")

    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    dados = {
        "sub": email,
        "exp": expiracao
    }

    return jwt.encode(dados, chave, algorithm=ALGORITHM)


def validar_token(token: str) -> str:
    chave = os.environ.get("JWT_SECRET_KEY")

    if not chave:
        raise RuntimeError("JWT_SECRET_KEY nao configurada")

    dados = jwt.decode(token, chave, algorithms=[ALGORITHM])
    return dados["sub"]
