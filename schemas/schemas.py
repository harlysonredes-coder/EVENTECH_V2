"""Schemas Pydantic: contratos de entrada e saída da API (também alimentam o Swagger)."""
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

PerfilUsuario = Literal["participante", "administrador", "organizador", "administrador/organizador"]
_PADRAO_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


def _normalizar_email(valor: str) -> str:
    return valor.strip().lower()


class _Resposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------- Usuários
class UsuarioCadastro(BaseModel):
    """Cadastro público. Só é aceito o perfil `participante`."""

    nome: str = Field(min_length=1, max_length=120, examples=["Maria Souza"])
    email: str = Field(pattern=_PADRAO_EMAIL, max_length=254, examples=["maria@exemplo.com"])
    senha: str = Field(min_length=8, max_length=128, examples=["SenhaForte@123"])
    perfil: str = Field(default="participante", examples=["participante"])

    _email = field_validator("email")(_normalizar_email)


class UsuarioAtualizar(BaseModel):
    """Atualização administrativa de um usuário (permite alterar o perfil)."""

    nome: str = Field(min_length=1, max_length=120)
    email: str = Field(pattern=_PADRAO_EMAIL, max_length=254)
    senha: str = Field(min_length=8, max_length=128)
    perfil: PerfilUsuario

    _email = field_validator("email")(_normalizar_email)


class UsuarioResposta(_Resposta):
    id_usuario: int
    nome: str
    email: str
    perfil: str


# ----------------------------------------------------------------------- Eventos
class EventoEntrada(BaseModel):
    titulo: str = Field(min_length=1, max_length=200, examples=["Semana de Tecnologia"])
    descricao: str = Field(min_length=1, max_length=2000, examples=["Palestras e oficinas"])
    data_evento: date = Field(examples=["2026-12-10"])
    capacidade: int = Field(gt=0, description="Número máximo de inscritos (> 0)", examples=[50])
    carga_horaria: int = Field(gt=0, description="Carga horária em horas (> 0)", examples=[8])


class EventoResposta(EventoEntrada, _Resposta):
    id_evento: int


# --------------------------------------------------------------------- Inscrições
class InscricaoEntrada(BaseModel):
    id_usuario: int = Field(gt=0, examples=[1])
    id_evento: int = Field(gt=0, examples=[1])


class InscricaoResposta(_Resposta):
    id_inscricao: int
    id_usuario: int
    id_evento: int
    status: str


# -------------------------------------------------------------------- Participações
class ParticipacaoEntrada(BaseModel):
    id_inscricao: int = Field(gt=0, examples=[1])
    presente: bool = Field(examples=[True])
    horas_obtidas: int = Field(ge=0, description="Não pode exceder a carga horária do evento", examples=[8])


class ParticipacaoResposta(_Resposta):
    id_participacao: int
    id_inscricao: int
    presente: bool
    horas_obtidas: int


# ---------------------------------------------------------------------- Certificados
class CertificadoEntrada(BaseModel):
    id_participacao: int = Field(gt=0, examples=[1])
    data_emissao: date = Field(examples=["2026-12-11"])


class CertificadoResposta(_Resposta):
    id_certificado: int
    id_participacao: int
    data_emissao: date


# ------------------------------------------------------------------------- Autenticação
class LoginEntrada(BaseModel):
    email: str = Field(examples=["maria@exemplo.com"])
    senha: str = Field(examples=["SenhaForte@123"])

    _email = field_validator("email")(_normalizar_email)


class TokenResposta(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class MensagemResposta(BaseModel):
    mensagem: str


class ErroResposta(BaseModel):
    """Formato único de erro de toda a API."""

    status: int = Field(examples=[404])
    codigo: str = Field(examples=["NAO_ENCONTRADO"])
    mensagem: str = Field(examples=["Evento não encontrado"])
    detalhes: list[dict] | None = Field(default=None, description="Presente em erros de validação (422)")
