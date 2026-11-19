"""Respostas de erro reutilizáveis na documentação OpenAPI."""
from schemas import ErroResposta

_ERRO = {"model": ErroResposta}

R401 = {401: {**_ERRO, "description": "Token ausente, inválido ou expirado"}}
R403 = {403: {**_ERRO, "description": "Autenticado, mas sem permissão para a ação"}}
R404 = {404: {**_ERRO, "description": "Recurso não encontrado"}}
R409 = {409: {**_ERRO, "description": "Conflito (duplicidade, sem vagas ou registro com dependências)"}}
R422 = {422: {**_ERRO, "description": "Dados inválidos ou regra de negócio violada"}}

ADMIN = {**R401, **R403}
