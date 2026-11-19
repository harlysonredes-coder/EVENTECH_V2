"""Handlers globais: todo erro da API sai no formato `ErroResposta`."""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.exceptions import AppError

logger = logging.getLogger("eventech")

_CODIGOS_HTTP = {
    401: "NAO_AUTENTICADO", 403: "ACESSO_NEGADO", 404: "NAO_ENCONTRADO",
    405: "METODO_NAO_PERMITIDO", 409: "CONFLITO", 422: "REQUISICAO_INVALIDA",
}


def _resposta(status: int, codigo: str, mensagem: str, detalhes=None, headers=None) -> JSONResponse:
    corpo = {"status": status, "codigo": codigo, "mensagem": mensagem, "detalhes": detalhes}
    return JSONResponse(status_code=status, content=corpo, headers=headers)


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError):
        return _resposta(exc.status_code, exc.codigo, exc.mensagem, headers=exc.headers)

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_: Request, exc: StarletteHTTPException):
        codigo = _CODIGOS_HTTP.get(exc.status_code, "ERRO_HTTP")
        return _resposta(exc.status_code, codigo, str(exc.detail), headers=getattr(exc, "headers", None))

    @app.exception_handler(RequestValidationError)
    async def _validacao(_: Request, exc: RequestValidationError):
        detalhes = [
            {"campo": ".".join(str(p) for p in e["loc"] if p != "body"), "erro": e["msg"]}
            for e in exc.errors()
        ]
        return _resposta(422, "REQUISICAO_INVALIDA", "Dados de entrada inválidos", detalhes)

    @app.exception_handler(IntegrityError)
    async def _integridade(_: Request, exc: IntegrityError):
        # Última barreira: a regra já deveria ter sido checada no serviço.
        logger.warning("Violação de integridade: %s", exc.orig)
        return _resposta(409, "CONFLITO", "A operação viola uma restrição de integridade dos dados")

    @app.exception_handler(Exception)
    async def _inesperado(_: Request, exc: Exception):
        logger.exception("Erro inesperado")
        return _resposta(500, "ERRO_INTERNO", "Erro interno do servidor")
