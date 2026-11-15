from sqlalchemy.orm import Session

import models
from core.exceptions import Conflito, RegraDeNegocio
from services.base import buscar_ou_404, remover, salvar


def obter(db: Session, id_evento: int):
    return buscar_ou_404(db, models.Evento, id_evento, "Evento não encontrado")


def contar_inscritos(db: Session, id_evento: int) -> int:
    return db.query(models.Inscricao).filter(models.Inscricao.id_evento == id_evento).count()


def criar(db: Session, dados):
    return salvar(db, models.Evento(**dados.model_dump()))


def atualizar(db: Session, id_evento: int, dados):
    evento = obter(db, id_evento)
    inscritos = contar_inscritos(db, id_evento)
    if dados.capacidade < inscritos:
        raise RegraDeNegocio(
            f"A capacidade ({dados.capacidade}) não pode ser menor que o número de inscritos ({inscritos})"
        )
    for campo, valor in dados.model_dump().items():
        setattr(evento, campo, valor)
    return salvar(db, evento)


def excluir(db: Session, id_evento: int) -> None:
    evento = obter(db, id_evento)
    if contar_inscritos(db, id_evento):
        raise Conflito("Evento possui inscrições; exclua-as antes de remover o evento")
    remover(db, evento)
