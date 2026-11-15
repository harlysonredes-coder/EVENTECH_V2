import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router
from core.config import obter_origens_cors
from core.database import criar_tabelas
from core.errors import registrar_handlers

DESCRICAO = """
API REST para gestão de **eventos acadêmicos**: usuários, eventos, inscrições,
participações e emissão de certificados.

## Autenticação
1. Cadastre-se em `POST /usuarios` (perfil *participante*) ou use um administrador criado via script.
2. Faça `POST /login` e copie o `access_token`.
3. Clique em **Authorize** e cole o token. Ele vale por 30 minutos.

## Padrão de erros
Toda resposta de erro segue o schema `ErroResposta`: `401` não autenticado, `403` sem permissão,
`404` não encontrado, `409` conflito (duplicidade, sem vagas, dependências) e `422` dados
inválidos ou regra de negócio violada.
"""

TAGS = [
    {"name": "Autenticação", "description": "Login e dados do usuário logado."},
    {"name": "Usuários", "description": "Cadastro e gestão de usuários."},
    {"name": "Eventos", "description": "Eventos acadêmicos (escrita restrita a administradores)."},
    {"name": "Inscrições", "description": "Inscrição de usuários em eventos, respeitando a capacidade."},
    {"name": "Participações", "description": "Presença e horas obtidas (administradores)."},
    {"name": "Certificados", "description": "Emissão de certificados (administradores)."},
    {"name": "Infraestrutura", "description": "Verificação de saúde do serviço."},
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    criar_tabelas()
    yield


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO)
    app = FastAPI(
        title="EVENTECH", version="2.0.0", description=DESCRICAO,
        openapi_tags=TAGS, lifespan=lifespan,
    )
    origens = obter_origens_cors()
    if origens:
        app.add_middleware(
            CORSMiddleware, allow_origins=origens, allow_methods=["*"], allow_headers=["*"],
        )
    registrar_handlers(app)
    app.include_router(router)

    @app.get("/health", tags=["Infraestrutura"], summary="Health check")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
