"""Exceções de domínio. Os serviços as lançam; um único handler as converte em HTTP."""


class AppError(Exception):
    status_code = 500
    codigo = "ERRO_INTERNO"

    def __init__(self, mensagem: str, headers: dict | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.headers = headers


class NaoAutenticado(AppError):
    status_code = 401
    codigo = "NAO_AUTENTICADO"

    def __init__(self, mensagem: str = "Autenticação necessária"):
        super().__init__(mensagem, headers={"WWW-Authenticate": "Bearer"})


class AcessoNegado(AppError):
    status_code = 403
    codigo = "ACESSO_NEGADO"


class NaoEncontrado(AppError):
    status_code = 404
    codigo = "NAO_ENCONTRADO"


class Conflito(AppError):
    """Estado atual do recurso impede a operação (duplicidade, sem vagas, dependências)."""

    status_code = 409
    codigo = "CONFLITO"


class RegraDeNegocio(AppError):
    """A requisição é válida sintaticamente, mas viola uma regra de negócio."""

    status_code = 422
    codigo = "REGRA_DE_NEGOCIO"
