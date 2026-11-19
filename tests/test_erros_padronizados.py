from tests.conftest import ADMIN

CHAVES = {"status", "codigo", "mensagem", "detalhes"}


def test_erro_404_segue_formato_padrao(ambiente, auth):
    client, _ = ambiente
    r = client.get("/eventos/9999", headers=auth(ADMIN))
    assert set(r.json()) == CHAVES and r.json()["status"] == 404 and r.json()["codigo"] == "NAO_ENCONTRADO"


def test_erro_422_lista_campos_invalidos(ambiente, auth):
    client, _ = ambiente
    r = client.post("/eventos", json={"titulo": ""}, headers=auth(ADMIN))
    assert r.status_code == 422 and set(r.json()) == CHAVES
    campos = {d["campo"] for d in r.json()["detalhes"]}
    assert {"titulo", "descricao", "data_evento", "capacidade", "carga_horaria"} <= campos


def test_erro_405_segue_formato_padrao(ambiente):
    client, _ = ambiente
    r = client.delete("/login")
    assert r.status_code == 405 and set(r.json()) == CHAVES


def test_rota_inexistente_retorna_404_padronizado(ambiente):
    client, _ = ambiente
    r = client.get("/nao-existe")
    assert r.status_code == 404 and set(r.json()) == CHAVES


def test_health_check_sem_autenticacao(ambiente):
    client, _ = ambiente
    assert client.get("/health").json() == {"status": "ok"}
