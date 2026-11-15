from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from api.deps import exigir_administrador, exigir_autenticacao
from api.docs import ADMIN, R401, R404, R409, R422
from core.database import get_db
from schemas import EventoEntrada, EventoResposta, MensagemResposta
from services import eventos

router = APIRouter(prefix="/eventos", tags=["Eventos"])


@router.post("", status_code=201, response_model=EventoResposta, summary="Criar evento (admin)",
             dependencies=[Depends(exigir_administrador)], responses={**ADMIN, **R422})
def criar_evento(dados: EventoEntrada, db: Session = Depends(get_db)):
    return eventos.criar(db, dados)


@router.get("", response_model=list[EventoResposta], summary="Listar eventos",
            dependencies=[Depends(exigir_autenticacao)], responses=R401)
def listar_eventos(db: Session = Depends(get_db)):
    return db.query(models.Evento).all()


@router.get("/{id_evento}", response_model=EventoResposta, summary="Buscar evento",
            dependencies=[Depends(exigir_autenticacao)], responses={**R401, **R404})
def buscar_evento(id_evento: int, db: Session = Depends(get_db)):
    return eventos.obter(db, id_evento)


@router.put("/{id_evento}", response_model=EventoResposta, summary="Atualizar evento (admin)",
            description="A capacidade não pode ser menor que o número de inscritos (422).",
            dependencies=[Depends(exigir_administrador)], responses={**ADMIN, **R404, **R422})
def atualizar_evento(id_evento: int, dados: EventoEntrada, db: Session = Depends(get_db)):
    return eventos.atualizar(db, id_evento, dados)


@router.delete("/{id_evento}", response_model=MensagemResposta, summary="Excluir evento (admin)",
               description="Retorna 409 se houver inscrições no evento.",
               dependencies=[Depends(exigir_administrador)], responses={**ADMIN, **R404, **R409})
def excluir_evento(id_evento: int, db: Session = Depends(get_db)):
    eventos.excluir(db, id_evento)
    return MensagemResposta(mensagem="Evento excluído com sucesso")
