import os, sys, json, tempfile
os.environ["JWT_SECRET_KEY"] = "k" * 40
os.chdir(tempfile.mkdtemp())                      # banco SQLite descartável
from fastapi.testclient import TestClient
from main import app
from core.database import SessionLocal
from core.security import criar_hash
from models import Usuario

try:
    from core.database import criar_tabelas; criar_tabelas()   # versão nova cria no startup
except ImportError:
    pass
with SessionLocal() as db:
    db.add(Usuario(nome="A", email="a@x.com", perfil="administrador", senha_hash=criar_hash("SenhaForte@1")))
    db.commit()
c = TestClient(app)
def login():
    r = c.post("/login", json={"email":"a@x.com","senha":"SenhaForte@1"})
    if r.status_code == 422:
        r = c.post("/login", params={"email":"a@x.com","senha":"SenhaForte@1"})
    return {"Authorization":"Bearer "+r.json()["access_token"]}
h = login()
ev = {"titulo":"E","descricao":"d","data_evento":"2026-12-01","capacidade":5,"carga_horaria":4}
def resumo(r):
    try: corpo = r.json()
    except Exception: corpo = r.text
    return f"{r.status_code} {json.dumps(corpo, ensure_ascii=False)[:110]}"

print("1. login com credenciais na URL      ->", c.post("/login", params={"email":"a@x.com","senha":"SenhaForte@1"}).status_code)
print("2. capacidade=0                      ->", resumo(c.post("/eventos", json={**ev,"capacidade":0}, headers=h)))
print("3. evento inexistente                ->", resumo(c.get("/eventos/999", headers=h)))
print("4. campo obrigatório ausente         ->", resumo(c.post("/eventos", json={"titulo":"x"}, headers=h)))
id_ev = c.post("/eventos", json=ev, headers=h).json()["id_evento"]
uid = c.get("/me", headers=h).json()["id_usuario"]
c.post("/inscricoes", json={"id_usuario":uid,"id_evento":id_ev}, headers=h)
print("5. inscrição duplicada               ->", resumo(c.post("/inscricoes", json={"id_usuario":uid,"id_evento":id_ev}, headers=h)))
print("6. excluir evento COM inscrição      ->", resumo(c.delete(f"/eventos/{id_ev}", headers=h)))
orfas = c.get("/inscricoes", headers=h).json()
print("   inscrições órfãs no banco depois  ->", len(orfas))
print("7. e-mail 'invalido' no cadastro     ->", c.post("/usuarios", json={"nome":"x","email":"invalido","perfil":"participante","senha":"1"}).status_code)
