def evento():
    return {"titulo":"Novo evento","descricao":"Descrição","data_evento":"2026-12-02","capacidade":10,"carga_horaria":3}


def test_sem_token_retorna_401(ambiente):
    client, _ = ambiente
    assert client.get("/usuarios").status_code == 401


def test_login_valido(ambiente):
    client, _ = ambiente
    resposta = client.post("/login", params={"email":"participante@teste.local","senha":"SenhaTeste@123"})
    assert resposta.status_code == 200
    assert resposta.json()["access_token"]


def test_login_invalido(ambiente):
    client, _ = ambiente
    assert client.post("/login",params={"email":"participante@teste.local","senha":"errada"}).status_code == 401


def test_participante_nao_cria_evento(ambiente, auth):
    client, _ = ambiente
    assert client.post("/eventos",json=evento(),headers=auth("participante@teste.local")).status_code == 403


def test_admin_cria_evento(ambiente, auth):
    client, _ = ambiente
    assert client.post("/eventos",json=evento(),headers=auth("admin@teste.local")).status_code == 201


def test_participante_nao_exclui_usuario(ambiente, auth):
    client, ids = ambiente
    assert client.delete(f"/usuarios/{ids['outro']}",headers=auth("participante@teste.local")).status_code == 403


def test_admin_exclusao_inexistente_retorna_404(ambiente, auth):
    client, _ = ambiente
    assert client.delete("/usuarios/999999",headers=auth("admin@teste.local")).status_code == 404


def test_participante_nao_exclui_inscricao_alheia(ambiente, auth):
    client, ids = ambiente
    assert client.delete(f"/inscricoes/{ids['inscricao']}",headers=auth("participante@teste.local")).status_code == 403


def test_cadastro_nao_permite_auto_admin(ambiente):
    client, _ = ambiente
    r=client.post("/usuarios",json={"nome":"Intruso","email":"intruso@teste.local","perfil":"administrador","senha":"SenhaTeste@123"})
    assert r.status_code == 403


def test_me_autenticado(ambiente, auth):
    client, _ = ambiente
    r=client.get("/me",headers=auth("participante@teste.local"))
    assert r.status_code == 200
    assert r.json()["perfil"] == "participante"
