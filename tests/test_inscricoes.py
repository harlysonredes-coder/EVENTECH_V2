from tests.conftest import ADMIN, OUTRO, PARTICIPANTE


def inscrever(client, auth, email, id_usuario, id_evento):
    return client.post("/inscricoes", json={"id_usuario": id_usuario, "id_evento": id_evento}, headers=auth(email))


def test_participante_se_inscreve(ambiente, auth):
    client, ids = ambiente
    r = inscrever(client, auth, PARTICIPANTE, ids["participante"], ids["evento"])
    assert r.status_code == 201 and r.json()["status"] == "Ativa"


def test_participante_nao_inscreve_terceiro(ambiente, auth):
    client, ids = ambiente
    assert inscrever(client, auth, PARTICIPANTE, ids["outro"], ids["evento"]).status_code == 403


def test_admin_inscreve_terceiro(ambiente, auth):
    client, ids = ambiente
    assert inscrever(client, auth, ADMIN, ids["participante"], ids["evento"]).status_code == 201


def test_inscricao_duplicada_retorna_409(ambiente, auth):
    client, ids = ambiente
    r = inscrever(client, auth, OUTRO, ids["outro"], ids["evento"])
    assert r.status_code == 409 and r.json()["mensagem"] == "Usuário já inscrito neste evento"


def test_inscricao_em_evento_inexistente_retorna_404(ambiente, auth):
    client, ids = ambiente
    assert inscrever(client, auth, PARTICIPANTE, ids["participante"], 9999).status_code == 404


def test_inscricao_para_usuario_inexistente_retorna_404(ambiente, auth):
    client, ids = ambiente
    assert inscrever(client, auth, ADMIN, 9999, ids["evento"]).status_code == 404


def test_inscricao_sem_vagas_retorna_409(ambiente, auth, evento_payload):
    client, ids = ambiente
    evento = client.post("/eventos", json=evento_payload(capacidade=1), headers=auth(ADMIN)).json()["id_evento"]
    assert inscrever(client, auth, OUTRO, ids["outro"], evento).status_code == 201
    r = inscrever(client, auth, PARTICIPANTE, ids["participante"], evento)
    assert r.status_code == 409 and r.json()["mensagem"] == "Evento sem vagas disponíveis"


def test_cancelar_inscricao_libera_vaga(ambiente, auth, evento_payload):
    client, ids = ambiente
    evento = client.post("/eventos", json=evento_payload(capacidade=1), headers=auth(ADMIN)).json()["id_evento"]
    id_insc = inscrever(client, auth, OUTRO, ids["outro"], evento).json()["id_inscricao"]
    assert client.delete(f"/inscricoes/{id_insc}", headers=auth(OUTRO)).status_code == 200
    assert inscrever(client, auth, PARTICIPANTE, ids["participante"], evento).status_code == 201


def test_participante_cancela_propria_inscricao(ambiente, auth):
    client, ids = ambiente
    assert client.delete(f"/inscricoes/{ids['inscricao']}", headers=auth(OUTRO)).status_code == 200


def test_admin_move_inscricao_para_evento_lotado_retorna_409(ambiente, auth, evento_payload):
    client, ids = ambiente
    lotado = client.post("/eventos", json=evento_payload(capacidade=1), headers=auth(ADMIN)).json()["id_evento"]
    inscrever(client, auth, PARTICIPANTE, ids["participante"], lotado)
    r = client.put(f"/inscricoes/{ids['inscricao']}", json={"id_usuario": ids["outro"], "id_evento": lotado},
                   headers=auth(ADMIN))
    assert r.status_code == 409


def test_listar_inscricoes_so_admin(ambiente, auth):
    client, _ = ambiente
    assert client.get("/inscricoes", headers=auth(ADMIN)).status_code == 200
    assert client.get("/inscricoes", headers=auth(PARTICIPANTE)).status_code == 403
