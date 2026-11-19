from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import exigir_administrador, usuario_atual
from api.docs import ADMIN, R401, R403, R404, R409, R422
from core.database import get_db
import models
from schemas import MensagemResposta, UsuarioAtualizar, UsuarioCadastro, UsuarioResposta
from services import usuarios

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post(
    "", status_code=201, response_model=UsuarioResposta, summary="Cadastro público de participante",
    description="Aberto, sem autenticação. Apenas o perfil `participante` é aceito; "
                "administradores são criados por `python -m scripts.criar_admin_local`.",
    responses={**R403, **R409, **R422},
)
def criar_usuario(dados: UsuarioCadastro, db: Session = Depends(get_db)):
    return usuarios.cadastrar_participante(db, dados)


@router.get("", response_model=list[UsuarioResposta], summary="Listar usuários (admin)",
            dependencies=[Depends(exigir_administrador)], responses=ADMIN)
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()


@router.get("/{id_usuario}", response_model=UsuarioResposta, summary="Buscar usuário",
            description="Participante só acessa o próprio registro; administrador acessa todos.",
            responses={**R401, **R403, **R404})
def buscar_usuario(id_usuario: int, db: Session = Depends(get_db), atual=Depends(usuario_atual)):
    usuarios.exigir_proprietario_ou_admin(id_usuario, atual)
    return usuarios.obter(db, id_usuario)


@router.put("/{id_usuario}", response_model=UsuarioResposta, summary="Atualizar usuário (admin)",
            dependencies=[Depends(exigir_administrador)], responses={**ADMIN, **R404, **R409, **R422})
def atualizar_usuario(id_usuario: int, dados: UsuarioAtualizar, db: Session = Depends(get_db)):
    return usuarios.atualizar(db, id_usuario, dados)


@router.delete("/{id_usuario}", response_model=MensagemResposta, summary="Excluir usuário (admin)",
               description="Retorna 409 se o usuário possuir inscrições.",
               dependencies=[Depends(exigir_administrador)], responses={**ADMIN, **R404, **R409})
def excluir_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuarios.excluir(db, id_usuario)
    return MensagemResposta(mensagem="Usuário excluído com sucesso")
