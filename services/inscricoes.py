from sqlalchemy.orm import Session

import models
from core.exceptions import Conflito
from services import eventos, usuarios
from services.base import buscar_ou_404, remover, salvar

STATUS_ATIVA = "Ativa"


def obter(db: Session, id_inscricao: int):
    return buscar_ou_404(db, models.Inscricao, id_inscricao, "Inscrição não encontrada")


def garantir_vaga(db: Session, evento) -> None:
    """Regra: o número de inscritos não pode ultrapassar a capacidade do evento."""
    if eventos.contar_inscritos(db, evento.id_evento) >= evento.capacidade:
        raise Conflito("Evento sem vagas disponíveis")


def garantir_sem_duplicidade(db: Session, id_usuario: int, id_evento: int, ignorar_id: int | None = None) -> None:
    """Regra: um usuário só pode ter uma inscrição por evento."""
    consulta = db.query(models.Inscricao).filter(
        models.Inscricao.id_usuario == id_usuario, models.Inscricao.id_evento == id_evento
    )
    if ignorar_id is not None:
        consulta = consulta.filter(models.Inscricao.id_inscricao != ignorar_id)
    if consulta.first():
        raise Conflito("Usuário já inscrito neste evento")


def criar(db: Session, dados):
    usuarios.obter(db, dados.id_usuario)
    evento = eventos.obter(db, dados.id_evento)
    garantir_sem_duplicidade(db, dados.id_usuario, dados.id_evento)
    garantir_vaga(db, evento)
    return salvar(db, models.Inscricao(
        id_usuario=dados.id_usuario, id_evento=dados.id_evento, status=STATUS_ATIVA,
    ))


def atualizar(db: Session, id_inscricao: int, dados):
    inscricao = obter(db, id_inscricao)
    usuarios.obter(db, dados.id_usuario)
    evento = eventos.obter(db, dados.id_evento)
    garantir_sem_duplicidade(db, dados.id_usuario, dados.id_evento, ignorar_id=id_inscricao)
    if inscricao.id_evento != dados.id_evento:
        garantir_vaga(db, evento)
    inscricao.id_usuario, inscricao.id_evento, inscricao.status = dados.id_usuario, dados.id_evento, STATUS_ATIVA
    return salvar(db, inscricao)


def excluir(db: Session, id_inscricao: int, atual) -> None:
    inscricao = obter(db, id_inscricao)
    usuarios.exigir_proprietario_ou_admin(inscricao.id_usuario, atual)
    if db.query(models.Participacao).filter(models.Participacao.id_inscricao == id_inscricao).first():
        raise Conflito("Inscrição possui participação registrada; exclua-a antes")
    remover(db, inscricao)
