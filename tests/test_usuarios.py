from tests.conftest import ADMIN, SENHA


def cadastro(**extra):
    return {"nome": "Novo", "email": "novo@teste.local", "senha": SENHA, **extra}


def test_cadastro_publico_cria_participante(ambiente):
    client, _ = ambiente
    r = client.post("/usuarios", json=cadastro())
    assert r.status_code == 201
    assert r.json()["perfil"] == "participante"
    assert "senha" not in r.json() and "senha_hash" not in r.json()


def test_cadastro_nao_permite_auto_admin(ambiente):
    client, _ = ambiente
    r = client.post("/usuarios", json=cadastro(perfil="administrador"))
    assert r.status_code == 403


def test_cadastro_email_duplicado_retorna_409(ambiente):
    client, _ = ambiente
    client.post("/usuarios", json=cadastro())
    assert client.post("/usuarios", json=cadastro()).status_code == 409


def test_cadastro_email_duplicado_ignora_caixa(ambiente):
    client, _ = ambiente
    client.post("/usuarios", json=cadastro())
    assert client.post("/usuarios", json=cadastro(email="NOVO@Teste.local")).status_code == 409


def test_cadastro_senha_curta_retorna_422(ambiente):
    client, _ = ambiente
    r = client.post("/usuarios", json=cadastro(senha="123"))
    assert r.status_code == 422
    assert r.json()["detalhes"][0]["campo"] == "senha"


def test_cadastro_email_invalido_retorna_422(ambiente):
    client, _ = ambiente
    assert client.post("/usuarios", json=cadastro(email="nao-e-email")).status_code == 422


def test_usuario_cadastrado_consegue_logar(ambiente):
    client, _ = ambiente
    client.post("/usuarios", json=cadastro())
    assert client.post("/login", json={"email": "novo@teste.local", "senha": SENHA}).status_code == 200


def test_admin_atualiza_usuario(ambiente, auth):
    client, ids = ambiente
    corpo = {"nome": "Renomeado", "email": "outro@teste.local", "senha": SENHA, "perfil": "participante"}
    r = client.put(f"/usuarios/{ids['outro']}", json=corpo, headers=auth(ADMIN))
    assert r.status_code == 200 and r.json()["nome"] == "Renomeado"


def test_admin_atualiza_para_email_existente_retorna_409(ambiente, auth):
    client, ids = ambiente
    corpo = {"nome": "X", "email": "participante@teste.local", "senha": SENHA, "perfil": "participante"}
    assert client.put(f"/usuarios/{ids['outro']}", json=corpo, headers=auth(ADMIN)).status_code == 409


def test_admin_nao_define_perfil_invalido(ambiente, auth):
    client, ids = ambiente
    corpo = {"nome": "X", "email": "x@teste.local", "senha": SENHA, "perfil": "superusuario"}
    assert client.put(f"/usuarios/{ids['outro']}", json=corpo, headers=auth(ADMIN)).status_code == 422


def test_admin_exclusao_inexistente_retorna_404(ambiente, auth):
    client, _ = ambiente
    assert client.delete("/usuarios/999999", headers=auth(ADMIN)).status_code == 404


def test_excluir_usuario_com_inscricao_retorna_409(ambiente, auth):
    client, ids = ambiente
    r = client.delete(f"/usuarios/{ids['outro']}", headers=auth(ADMIN))
    assert r.status_code == 409


def test_admin_exclui_usuario_sem_dependencias(ambiente, auth):
    client, ids = ambiente
    assert client.delete(f"/usuarios/{ids['participante']}", headers=auth(ADMIN)).status_code == 200
