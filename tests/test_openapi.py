"""Garante que o Swagger/OpenAPI continua fiel ao comportamento real da API."""
import pytest

from main import app

PUBLICOS = {("/login", "post"), ("/usuarios", "post"), ("/health", "get")}


@pytest.fixture(scope="module")
def spec():
    return app.openapi()


def test_esquema_de_autenticacao_bearer_jwt_documentado(spec):
    esquema = spec["components"]["securitySchemes"]["BearerAuth"]
    assert esquema["scheme"] == "bearer" and esquema["bearerFormat"] == "JWT"


def test_endpoints_protegidos_exigem_security_e_documentam_401(spec):
    for caminho, operacoes in spec["paths"].items():
        for metodo, op in operacoes.items():
            if (caminho, metodo) in PUBLICOS:
                assert "security" not in op
            else:
                assert "security" in op, f"{metodo.upper()} {caminho} sem security"
                assert "401" in op["responses"], f"{metodo.upper()} {caminho} sem 401"


def test_todos_os_endpoints_tem_resumo_e_tag(spec):
    for caminho, operacoes in spec["paths"].items():
        for metodo, op in operacoes.items():
            assert op.get("summary") and op.get("tags"), f"{metodo.upper()} {caminho}"


def test_422_documentado_usa_o_formato_padrao_de_erro(spec):
    for operacoes in spec["paths"].values():
        for op in operacoes.values():
            if "422" in op["responses"]:
                ref = op["responses"]["422"]["content"]["application/json"]["schema"]["$ref"]
                assert ref.endswith("/ErroResposta")
