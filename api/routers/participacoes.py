from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from api.deps import exigir_administrador
from api.docs import ADMIN, R404, R409, R422
from core.database import get_db
from schemas import MensagemResposta, ParticipacaoEntrada, ParticipacaoResposta
from services import participacoes

router = APIRouter(
    prefix="/participacoes", tags=["Participações"], dependencies=[Depends(exigir_administrador)],
)


@router.post("", status_code=201, response_model=ParticipacaoResposta, summary="Registrar participação (admin)",
             description="Horas obtidas devem estar entre 0 e a carga horária do evento (422).",
             responses={**ADMIN, **R404, **R409, **R422})
def criar_participacao(dados: ParticipacaoEntrada, db: Session = Depends(get_db)):
    return participacoes.criar(db, dados)


@router.get("", response_model=list[ParticipacaoResposta], summary="Listar participações (admin)", responses=ADMIN)
def listar_participacoes(db: Session = Depends(get_db)):
    return db.query(models.Participacao).all()


@router.get("/{id_participacao}", response_model=ParticipacaoResposta, summary="Buscar participação (admin)",
            responses={**ADMIN, **R404})
def buscar_participacao(id_participacao: int, db: Session = Depends(get_db)):
    return participacoes.obter(db, id_participacao)


@router.put("/{id_participacao}", response_model=ParticipacaoResposta, summary="Atualizar participação (admin)",
            responses={**ADMIN, **R404, **R409, **R422})
def atualizar_participacao(id_participacao: int, dados: ParticipacaoEntrada, db: Session = Depends(get_db)):
    return participacoes.atualizar(db, id_participacao, dados)


@router.delete("/{id_participacao}", response_model=MensagemResposta, summary="Excluir participação (admin)",
               description="Retorna 409 se já houver certificado emitido.", responses={**ADMIN, **R404, **R409})
def excluir_participacao(id_participacao: int, db: Session = Depends(get_db)):
    participacoes.excluir(db, id_participacao)
    return MensagemResposta(mensagem="Participação excluída com sucesso")
