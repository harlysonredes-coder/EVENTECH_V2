from sqlalchemy.orm import Session

import models
from core.exceptions import Conflito, RegraDeNegocio
from services import eventos, inscricoes, participacoes
from services.base import buscar_ou_404, remover, salvar


def obter(db: Session, id_certificado: int):
    return buscar_ou_404(db, models.Certificado, id_certificado, "Certificado não encontrado")


def validar_elegibilidade(participacao, evento) -> None:
    """Regras de emissão: presença confirmada e carga horária integralmente cumprida."""
    if not participacao.presente:
        raise RegraDeNegocio("Participante não esteve presente no evento")
    if participacao.horas_obtidas < evento.carga_horaria:
        raise RegraDeNegocio("Carga horária insuficiente para emissão do certificado")


def _validar_para_emissao(db: Session, id_participacao: int, ignorar_id: int | None = None) -> None:
    participacao = participacoes.obter(db, id_participacao)
    evento = eventos.obter(db, inscricoes.obter(db, participacao.id_inscricao).id_evento)
    validar_elegibilidade(participacao, evento)
    consulta = db.query(models.Certificado).filter(models.Certificado.id_participacao == id_participacao)
    if ignorar_id is not None:
        consulta = consulta.filter(models.Certificado.id_certificado != ignorar_id)
    if consulta.first():
        raise Conflito("Certificado já emitido para esta participação")


def emitir(db: Session, dados):
    _validar_para_emissao(db, dados.id_participacao)
    return salvar(db, models.Certificado(**dados.model_dump()))


def atualizar(db: Session, id_certificado: int, dados):
    certificado = obter(db, id_certificado)
    _validar_para_emissao(db, dados.id_participacao, ignorar_id=id_certificado)
    certificado.id_participacao, certificado.data_emissao = dados.id_participacao, dados.data_emissao
    return salvar(db, certificado)


def excluir(db: Session, id_certificado: int) -> None:
    remover(db, obter(db, id_certificado))
