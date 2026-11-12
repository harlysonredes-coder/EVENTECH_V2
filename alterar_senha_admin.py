
from getpass import getpass
from core.database import SessionLocal
from core.security import criar_hash
from models import Usuario

email = "admin.eventech@example.com"

nova_senha = getpass("Digite a nova senha: ")

if len(nova_senha) < 8:
    raise SystemExit("A senha precisa ter pelo menos 8 caracteres.")

with SessionLocal() as db:
    admin = db.query(Usuario).filter(
        Usuario.email == email,
        Usuario.perfil == "administrador"
    ).first()

    if not admin:
        raise SystemExit("Administrador não encontrado.")

    admin.senha_hash = criar_hash(nova_senha)
    db.commit()

print("Senha do administrador atualizada com sucesso!")