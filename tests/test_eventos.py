from tests.conftest import ADMIN, PARTICIPANTE


def test_admin_cria_evento(ambiente, auth, evento_payload):
    client, _ = ambiente
    r = client.post("/eventos", json=evento_payload(), headers=auth(ADMIN))
    assert r.status_code == 201 and r.json()["id_evento"]


def test_evento_capacidade_zero_retorna_422(ambiente, auth, evento_payload):
    client, _ = ambiente
    assert client.post("/eventos", json=evento_payload(capacidade=0), headers=auth(ADMIN)).status_code == 422


def test_evento_carga_horaria_negativa_retorna_422(ambiente, auth, evento_payload):
    client, _ = ambiente
    assert client.post("/eventos", json=evento_payload(carga_horaria=-1), headers=auth(ADMIN)).status_code == 422


def test_evento_data_invalida_retorna_422(ambiente, auth, evento_payload):
    client, _ = ambiente
    assert client.post("/eventos", json=evento_payload(data_evento="31/12/2026"), headers=auth(ADMIN)).status_code == 422


def test_participante_lista_e_busca_eventos(ambiente, auth):
    client, ids = ambiente
    assert len(client.get("/eventos", headers=auth(PARTICIPANTE)).json()) == 1
    assert client.get(f"/eventos/{ids['evento']}", headers=auth(PARTICIPANTE)).status_code == 200


def test_buscar_evento_inexistente_retorna_404(ambiente, auth):
    client, _ = ambiente
    r = client.get("/eventos/9999", headers=auth(PARTICIPANTE))
    assert r.status_code == 404 and r.json()["mensagem"] == "Evento não encontrado"


def test_admin_atualiza_evento(ambiente, auth, evento_payload):
    client, ids = ambiente
    r = client.put(f"/eventos/{ids['evento']}", json=evento_payload(titulo="Atualizado"), headers=auth(ADMIN))
    assert r.status_code == 200 and r.json()["titulo"] == "Atualizado"


def test_reduzir_capacidade_abaixo_dos_inscritos_retorna_422(ambiente, auth, evento_payload):
    """Regra: o evento tem 1 inscrito; capacidade 1 é válida, mas após 2 inscritos não seria."""
    client, ids = ambiente
    client.post("/inscricoes", json={"id_usuario": ids["participante"], "id_evento": ids["evento"]},
                headers=auth(PARTICIPANTE))
    r = client.put(f"/eventos/{ids['evento']}", json=evento_payload(capacidade=1), headers=auth(ADMIN))
    assert r.status_code == 422 and r.json()["codigo"] == "REGRA_DE_NEGOCIO"


def test_excluir_evento_com_inscricoes_retorna_409(ambiente, auth):
    client, ids = ambiente
    assert client.delete(f"/eventos/{ids['evento']}", headers=auth(ADMIN)).status_code == 409


def test_excluir_evento_sem_inscricoes(ambiente, auth, evento_payload):
    client, _ = ambiente
    novo = client.post("/eventos", json=evento_payload(), headers=auth(ADMIN)).json()["id_evento"]
    assert client.delete(f"/eventos/{novo}", headers=auth(ADMIN)).status_code == 200
