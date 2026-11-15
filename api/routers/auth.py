from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import usuario_atual
from api.docs import R401, R422
from core.database import get_db
from core.exceptions import NaoAutenticado
from core.security import criar_token, verificar_senha
from schemas import LoginEntrada, TokenResposta, UsuarioResposta
from services import usuarios

router = APIRouter(tags=["Autenticação"])


@router.post(
    "/login", response_model=TokenResposta, summary="Autenticar e obter token JWT",
    description="Valida e-mail e senha e devolve um JWT (validade padrão de 30 minutos). "
                "Credenciais trafegam no corpo da requisição, nunca na URL.",
    responses={**R401, **R422},
)
def login(dados: LoginEntrada, db: Session = Depends(get_db)):
    usuario = usuarios.buscar_por_email(db, dados.email)
    if usuario is None or not verificar_senha(dados.senha, usuario.senha_hash):
        raise NaoAutenticado("Email ou senha incorretos")
    return TokenResposta(access_token=criar_token(usuario.email))


@router.get("/me", response_model=UsuarioResposta, summary="Dados do usuário autenticado", responses=R401)
def me(atual=Depends(usuario_atual)):
    return atual
