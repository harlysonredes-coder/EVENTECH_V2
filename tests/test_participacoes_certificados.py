import pytest

from tests.conftest import ADMIN, PARTICIPANTE


@pytest.fixture
def registrar(ambiente, auth):
    """Registra participação na inscrição semeada (evento de 4h)."""
    client, ids = ambiente

    def _registrar(presente=True, horas=4):
        return client.post(
            "/participacoes",
            json={"id_inscricao": ids["inscricao"], "presente": presente, "horas_obtidas": horas},
            headers=auth(ADMIN),
        )
    return _registrar


def emitir(client, auth, id_participacao):
    return client.post("/certificados", json={"id_participacao": id_participacao, "data_emissao": "2026-12-02"},
                       headers=auth(ADMIN))


def test_admin_registra_participacao(registrar):
    r = registrar()
    assert r.status_code == 201 and r.json()["presente"] is True


def test_participacao_duplicada_retorna_409(registrar):
    registrar()
    assert registrar().status_code == 409


def test_horas_acima_da_carga_horaria_retorna_422(registrar):
    r = registrar(horas=5)
    assert r.status_code == 422
    assert "carga horária" in r.json()["mensagem"]


def test_horas_negativas_retorna_422(registrar):
    assert registrar(horas=-1).status_code == 422


def test_participacao_em_inscricao_inexistente_retorna_404(ambiente, auth):
    client, _ = ambiente
    r = client.post("/participacoes", json={"id_inscricao": 9999, "presente": True, "horas_obtidas": 1},
                    headers=auth(ADMIN))
    assert r.status_code == 404


def test_participante_nao_registra_participacao(ambiente, auth):
    client, ids = ambiente
    r = client.post("/participacoes", json={"id_inscricao": ids["inscricao"], "presente": True, "horas_obtidas": 1},
                    headers=auth(PARTICIPANTE))
    assert r.status_code == 403


def test_emite_certificado_quando_elegivel(ambiente, auth, registrar):
    client, _ = ambiente
    id_part = registrar().json()["id_participacao"]
    r = emitir(client, auth, id_part)
    assert r.status_code == 201 and r.json()["id_participacao"] == id_part


def test_certificado_negado_para_ausente(ambiente, auth, registrar):
    client, _ = ambiente
    id_part = registrar(presente=False, horas=0).json()["id_participacao"]
    r = emitir(client, auth, id_part)
    assert r.status_code == 422 and r.json()["mensagem"] == "Participante não esteve presente no evento"


def test_certificado_negado_por_carga_horaria_insuficiente(ambiente, auth, registrar):
    client, _ = ambiente
    id_part = registrar(horas=3).json()["id_participacao"]
    r = emitir(client, auth, id_part)
    assert r.status_code == 422 and "insuficiente" in r.json()["mensagem"]


def test_certificado_duplicado_retorna_409(ambiente, auth, registrar):
    client, _ = ambiente
    id_part = registrar().json()["id_participacao"]
    emitir(client, auth, id_part)
    assert emitir(client, auth, id_part).status_code == 409


def test_certificado_para_participacao_inexistente_retorna_404(ambiente, auth):
    client, _ = ambiente
    assert emitir(client, auth, 9999).status_code == 404


def test_excluir_participacao_com_certificado_retorna_409(ambiente, auth, registrar):
    client, _ = ambiente
    id_part = registrar().json()["id_participacao"]
    emitir(client, auth, id_part)
    assert client.delete(f"/participacoes/{id_part}", headers=auth(ADMIN)).status_code == 409


def test_excluir_inscricao_com_participacao_retorna_409(ambiente, auth, registrar):
    client, ids = ambiente
    registrar()
    assert client.delete(f"/inscricoes/{ids['inscricao']}", headers=auth(ADMIN)).status_code == 409


def test_fluxo_completo_e_exclusao_em_cascata_manual(ambiente, auth, registrar):
    """Exclui na ordem correta: certificado -> participação -> inscrição."""
    client, ids = ambiente
    id_part = registrar().json()["id_participacao"]
    id_cert = emitir(client, auth, id_part).json()["id_certificado"]
    assert client.delete(f"/certificados/{id_cert}", headers=auth(ADMIN)).status_code == 200
    assert client.delete(f"/participacoes/{id_part}", headers=auth(ADMIN)).status_code == 200
    assert client.delete(f"/inscricoes/{ids['inscricao']}", headers=auth(ADMIN)).status_code == 200


def test_admin_atualiza_participacao(ambiente, auth, registrar):
    client, ids = ambiente
    id_part = registrar(horas=2).json()["id_participacao"]
    corpo = {"id_inscricao": ids["inscricao"], "presente": True, "horas_obtidas": 4}
    r = client.put(f"/participacoes/{id_part}", json=corpo, headers=auth(ADMIN))
    assert r.status_code == 200 and r.json()["horas_obtidas"] == 4


def test_atualizar_participacao_com_horas_invalidas_retorna_422(ambiente, auth, registrar):
    client, ids = ambiente
    id_part = registrar().json()["id_participacao"]
    corpo = {"id_inscricao": ids["inscricao"], "presente": True, "horas_obtidas": 99}
    assert client.put(f"/participacoes/{id_part}", json=corpo, headers=auth(ADMIN)).status_code == 422


def test_atualizar_participacao_inexistente_retorna_404(ambiente, auth):
    client, ids = ambiente
    corpo = {"id_inscricao": ids["inscricao"], "presente": True, "horas_obtidas": 1}
    assert client.put("/participacoes/9999", json=corpo, headers=auth(ADMIN)).status_code == 404


def test_admin_atualiza_data_do_certificado(ambiente, auth, registrar):
    client, _ = ambiente
    id_part = registrar().json()["id_participacao"]
    id_cert = emitir(client, auth, id_part).json()["id_certificado"]
    r = client.put(f"/certificados/{id_cert}", json={"id_participacao": id_part, "data_emissao": "2026-12-20"},
                   headers=auth(ADMIN))
    assert r.status_code == 200 and r.json()["data_emissao"] == "2026-12-20"


def test_buscar_certificado_inexistente_retorna_404(ambiente, auth):
    client, _ = ambiente
    assert client.get("/certificados/9999", headers=auth(ADMIN)).status_code == 404
