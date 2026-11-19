from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from api.deps import exigir_administrador, usuario_atual
from api.docs import ADMIN, R401, R403, R404, R409, R422
from core.database import get_db
from schemas import InscricaoEntrada, InscricaoResposta, MensagemResposta
from services import inscricoes, usuarios

router = APIRouter(prefix="/inscricoes", tags=["Inscrições"])


@router.post("", status_code=201, response_model=InscricaoResposta, summary="Inscrever em evento",
             description="Participante só inscreve a si mesmo. Retorna 409 se já inscrito ou se não houver vagas.",
             responses={**R401, **R403, **R404, **R409, **R422})
def criar_inscricao(dados: InscricaoEntrada, db: Session = Depends(get_db), atual=Depends(usuario_atual)):
    usuarios.exigir_proprietario_ou_admin(dados.id_usuario, atual)
    return inscricoes.criar(db, dados)


@router.get("", response_model=list[InscricaoResposta], summary="Listar inscrições (admin)",
            dependencies=[Depends(exigir_administrador)], responses=ADMIN)
def listar_inscricoes(db: Session = Depends(get_db)):
    return db.query(models.Inscricao).all()


@router.get("/{id_inscricao}", response_model=InscricaoResposta, summary="Buscar inscrição",
            description="Participante só acessa a própria inscrição.",
            responses={**R401, **R403, **R404})
def buscar_inscricao(id_inscricao: int, db: Session = Depends(get_db), atual=Depends(usuario_atual)):
    inscricao = inscricoes.obter(db, id_inscricao)
    usuarios.exigir_proprietario_ou_admin(inscricao.id_usuario, atual)
    return inscricao


@router.put("/{id_inscricao}", response_model=InscricaoResposta, summary="Atualizar inscrição (admin)",
            dependencies=[Depends(exigir_administrador)], responses={**ADMIN, **R404, **R409, **R422})
def atualizar_inscricao(id_inscricao: int, dados: InscricaoEntrada, db: Session = Depends(get_db)):
    return inscricoes.atualizar(db, id_inscricao, dados)


@router.delete("/{id_inscricao}", response_model=MensagemResposta, summary="Cancelar inscrição",
               description="Participante só exclui a própria inscrição. Retorna 409 se já houver participação.",
               responses={**R401, **R403, **R404, **R409})
def excluir_inscricao(id_inscricao: int, db: Session = Depends(get_db), atual=Depends(usuario_atual)):
    inscricoes.excluir(db, id_inscricao, atual)
    return MensagemResposta(mensagem="Inscrição excluída com sucesso")
