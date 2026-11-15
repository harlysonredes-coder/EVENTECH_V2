from sqlalchemy.orm import Session

import models
from core.exceptions import Conflito, RegraDeNegocio
from services import eventos, inscricoes
from services.base import buscar_ou_404, remover, salvar


def obter(db: Session, id_participacao: int):
    return buscar_ou_404(db, models.Participacao, id_participacao, "Participação não encontrada")


def validar_horas(horas_obtidas: int, evento) -> None:
    """Regra: horas obtidas ficam entre 0 e a carga horária do evento."""
    if horas_obtidas < 0:
        raise RegraDeNegocio("As horas obtidas não podem ser negativas")
    if horas_obtidas > evento.carga_horaria:
        raise RegraDeNegocio("As horas obtidas não podem ser maiores que a carga horária do evento")


def _garantir_unica(db: Session, id_inscricao: int, ignorar_id: int | None = None) -> None:
    consulta = db.query(models.Participacao).filter(models.Participacao.id_inscricao == id_inscricao)
    if ignorar_id is not None:
        consulta = consulta.filter(models.Participacao.id_participacao != ignorar_id)
    if consulta.first():
        raise Conflito("Participação já registrada para esta inscrição")


def criar(db: Session, dados):
    inscricao = inscricoes.obter(db, dados.id_inscricao)
    _garantir_unica(db, dados.id_inscricao)
    validar_horas(dados.horas_obtidas, eventos.obter(db, inscricao.id_evento))
    return salvar(db, models.Participacao(**dados.model_dump()))


def atualizar(db: Session, id_participacao: int, dados):
    participacao = obter(db, id_participacao)
    inscricao = inscricoes.obter(db, dados.id_inscricao)
    _garantir_unica(db, dados.id_inscricao, ignorar_id=id_participacao)
    validar_horas(dados.horas_obtidas, eventos.obter(db, inscricao.id_evento))
    for campo, valor in dados.model_dump().items():
        setattr(participacao, campo, valor)
    return salvar(db, participacao)


def excluir(db: Session, id_participacao: int) -> None:
    participacao = obter(db, id_participacao)
    if db.query(models.Certificado).filter(models.Certificado.id_participacao == id_participacao).first():
        raise Conflito("Participação possui certificado emitido; exclua-o antes")
    remover(db, participacao)
