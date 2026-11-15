from sqlalchemy.orm import Session

import models
from core.exceptions import AcessoNegado, Conflito
from core.security import criar_hash
from services.base import buscar_ou_404, remover, salvar

PERFIS_ADMIN = ("administrador", "organizador", "administrador/organizador")


def eh_admin(usuario) -> bool:
    return usuario.perfil in PERFIS_ADMIN


def buscar_por_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()


def obter(db: Session, id_usuario: int):
    return buscar_ou_404(db, models.Usuario, id_usuario, "Usuário não encontrado")


def _garantir_email_livre(db: Session, email: str, ignorar_id: int | None = None) -> None:
    consulta = db.query(models.Usuario).filter(models.Usuario.email == email)
    if ignorar_id is not None:
        consulta = consulta.filter(models.Usuario.id_usuario != ignorar_id)
    if consulta.first():
        raise Conflito("E-mail já cadastrado")


def cadastrar_participante(db: Session, dados):
    if dados.perfil != "participante":
        raise AcessoNegado("Cadastro público permite apenas participante")
    _garantir_email_livre(db, dados.email)
    return salvar(db, models.Usuario(
        nome=dados.nome, email=dados.email, perfil="participante", senha_hash=criar_hash(dados.senha),
    ))


def atualizar(db: Session, id_usuario: int, dados):
    usuario = obter(db, id_usuario)
    _garantir_email_livre(db, dados.email, ignorar_id=id_usuario)
    usuario.nome, usuario.email, usuario.perfil = dados.nome, dados.email, dados.perfil
    usuario.senha_hash = criar_hash(dados.senha)
    return salvar(db, usuario)


def excluir(db: Session, id_usuario: int) -> None:
    usuario = obter(db, id_usuario)
    possui_inscricoes = db.query(models.Inscricao).filter(
        models.Inscricao.id_usuario == id_usuario
    ).first()
    if possui_inscricoes:
        raise Conflito("Usuário possui inscrições; exclua-as antes de remover o usuário")
    remover(db, usuario)


def exigir_proprietario_ou_admin(id_dono: int, atual) -> None:
    if atual.id_usuario != id_dono and not eh_admin(atual):
        raise AcessoNegado("Acesso não permitido a recurso de outro usuário")
