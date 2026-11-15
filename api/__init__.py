from fastapi import APIRouter

from .routers import auth, certificados, eventos, inscricoes, participacoes, usuarios

router = APIRouter()
for modulo in (auth, usuarios, eventos, inscricoes, participacoes, certificados):
    router.include_router(modulo.router)
