"""Redefine a senha de um administrador. Uso: python -m scripts.alterar_senha_admin <email>"""
import sys
from getpass import getpass

from core.database import SessionLocal
from core.security import criar_hash
from models import Usuario


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python -m scripts.alterar_senha_admin <email>")
    email = sys.argv[1].strip().lower()
    nova_senha = getpass("Digite a nova senha: ")
    if len(nova_senha) < 8:
        raise SystemExit("A senha precisa ter pelo menos 8 caracteres.")
    with SessionLocal() as db:
        admin = db.query(Usuario).filter(Usuario.email == email, Usuario.perfil == "administrador").first()
        if not admin:
            raise SystemExit("Administrador não encontrado.")
        admin.senha_hash = criar_hash(nova_senha)
        db.commit()
    print("Senha do administrador atualizada com sucesso!")


if __name__ == "__main__":
    main()
