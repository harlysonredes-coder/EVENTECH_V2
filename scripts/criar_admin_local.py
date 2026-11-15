"""Cria um administrador pelo terminal, sem expor cadastro administrativo na API.

Uso:  python -m scripts.criar_admin_local
Não-interativo (deploy): defina ADMIN_EMAIL, ADMIN_NOME e ADMIN_SENHA no ambiente.
"""
import os
from getpass import getpass

from core.database import SessionLocal, criar_tabelas
from core.security import criar_hash
from models import Usuario


def main() -> None:
    email = (os.environ.get("ADMIN_EMAIL") or input("E-mail do administrador: ")).strip().lower()
    nome = (os.environ.get("ADMIN_NOME") or input("Nome: ")).strip()
    senha = os.environ.get("ADMIN_SENHA") or getpass("Senha: ")
    if not email or not nome or len(senha) < 8:
        raise SystemExit("Informe nome, e-mail e senha com pelo menos 8 caracteres")
    criar_tabelas()
    with SessionLocal() as db:
        if db.query(Usuario).filter(Usuario.email == email).first():
            raise SystemExit("E-mail já cadastrado; nenhuma alteração realizada")
        db.add(Usuario(nome=nome, email=email, perfil="administrador", senha_hash=criar_hash(senha)))
        db.commit()
    print("Administrador criado com sucesso")


if __name__ == "__main__":
    main()
