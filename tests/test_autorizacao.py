from tests.conftest import ADMIN, OUTRO, PARTICIPANTE, SENHA


def test_sem_token_retorna_401(ambiente):
    client, _ = ambiente
    r = client.get("/usuarios")
    assert r.status_code == 401
    assert r.headers["www-authenticate"] == "Bearer"


def test_token_invalido_retorna_401(ambiente):
    client, _ = ambiente
    r = client.get("/eventos", headers={"Authorization": "Bearer token.falso.aqui"})
    assert r.status_code == 401
    assert r.json()["codigo"] == "NAO_AUTENTICADO"


def test_login_valido(ambiente):
    client, _ = ambiente
    r = client.post("/login", json={"email": PARTICIPANTE, "senha": SENHA})
    assert r.status_code == 200
    assert r.json()["access_token"]
    assert r.json()["token_type"] == "bearer"


def test_login_senha_errada_retorna_401(ambiente):
    client, _ = ambiente
    assert client.post("/login", json={"email": PARTICIPANTE, "senha": "errada"}).status_code == 401


def test_login_usuario_inexistente_retorna_401(ambiente):
    client, _ = ambiente
    assert client.post("/login", json={"email": "ninguem@teste.local", "senha": SENHA}).status_code == 401


def test_login_sem_corpo_retorna_422(ambiente):
    client, _ = ambiente
    assert client.post("/login").status_code == 422


def test_login_nao_aceita_credenciais_na_url(ambiente):
    """Regressão: credenciais na query string vazam em logs; só o corpo é aceito."""
    client, _ = ambiente
    r = client.post("/login", params={"email": PARTICIPANTE, "senha": SENHA})
    assert r.status_code == 422


def test_me_autenticado(ambiente, auth):
    client, _ = ambiente
    r = client.get("/me", headers=auth(PARTICIPANTE))
    assert r.status_code == 200
    assert r.json()["perfil"] == "participante"
    assert "senha_hash" not in r.json()


def test_participante_nao_cria_evento(ambiente, auth, evento_payload):
    client, _ = ambiente
    assert client.post("/eventos", json=evento_payload(), headers=auth(PARTICIPANTE)).status_code == 403


def test_participante_nao_lista_usuarios(ambiente, auth):
    client, _ = ambiente
    assert client.get("/usuarios", headers=auth(PARTICIPANTE)).status_code == 403


def test_participante_nao_acessa_certificados(ambiente, auth):
    client, _ = ambiente
    assert client.get("/certificados", headers=auth(PARTICIPANTE)).status_code == 403
    assert client.get("/participacoes", headers=auth(PARTICIPANTE)).status_code == 403


def test_participante_nao_exclui_usuario(ambiente, auth):
    client, ids = ambiente
    assert client.delete(f"/usuarios/{ids['outro']}", headers=auth(PARTICIPANTE)).status_code == 403


def test_participante_nao_exclui_inscricao_alheia(ambiente, auth):
    client, ids = ambiente
    assert client.delete(f"/inscricoes/{ids['inscricao']}", headers=auth(PARTICIPANTE)).status_code == 403


def test_participante_nao_le_inscricao_alheia(ambiente, auth):
    client, ids = ambiente
    assert client.get(f"/inscricoes/{ids['inscricao']}", headers=auth(PARTICIPANTE)).status_code == 403


def test_participante_le_propria_inscricao(ambiente, auth):
    client, ids = ambiente
    assert client.get(f"/inscricoes/{ids['inscricao']}", headers=auth(OUTRO)).status_code == 200


def test_participante_nao_le_outro_usuario_mas_le_a_si(ambiente, auth):
    client, ids = ambiente
    assert client.get(f"/usuarios/{ids['outro']}", headers=auth(PARTICIPANTE)).status_code == 403
    assert client.get(f"/usuarios/{ids['participante']}", headers=auth(PARTICIPANTE)).status_code == 200


def test_admin_lista_usuarios(ambiente, auth):
    client, _ = ambiente
    r = client.get("/usuarios", headers=auth(ADMIN))
    assert r.status_code == 200 and len(r.json()) == 3
