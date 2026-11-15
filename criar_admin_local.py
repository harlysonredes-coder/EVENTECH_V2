"""Cria administrador local via terminal, sem expor cadastro administrativo na API."""
from getpass import getpass
from core.database import SessionLocal
from core.security import criar_hash
from models import Usuario

email = input("E-mail do administrador: ").strip().lower()
nome = input("Nome: ").strip()
senha = getpass("Senha: ")
if not email or not nome or len(senha) < 8:
    raise SystemExit("Informe nome, e-mail e senha com pelo menos 8 caracteres")
with SessionLocal() as db:
    if db.query(Usuario).filter(Usuario.email == email).first():
        raise SystemExit("E-mail já cadastrado; nenhuma alteração realizada")
    db.add(Usuario(nome=nome, email=email, perfil="administrador", senha_hash=criar_hash(senha)))
    db.commit()
print("Administrador criado no banco local")
