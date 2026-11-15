"""Testes unitários das regras de negócio, sem HTTP."""
from datetime import date
from types import SimpleNamespace

import pytest

from core.exceptions import Conflito, RegraDeNegocio
from models import Evento, Inscricao, Usuario
from services import certificados, inscricoes, participacoes

EVENTO = SimpleNamespace(carga_horaria=4)


def test_horas_dentro_do_limite_sao_aceitas():
    participacoes.validar_horas(0, EVENTO)
    participacoes.validar_horas(4, EVENTO)


@pytest.mark.parametrize("horas", [-1, 5])
def test_horas_fora_do_limite_sao_rejeitadas(horas):
    with pytest.raises(RegraDeNegocio):
        participacoes.validar_horas(horas, EVENTO)


def test_elegibilidade_exige_presenca():
    with pytest.raises(RegraDeNegocio, match="presente"):
        certificados.validar_elegibilidade(SimpleNamespace(presente=False, horas_obtidas=4), EVENTO)


def test_elegibilidade_exige_carga_horaria_completa():
    with pytest.raises(RegraDeNegocio, match="insuficiente"):
        certificados.validar_elegibilidade(SimpleNamespace(presente=True, horas_obtidas=3), EVENTO)


def test_elegibilidade_aceita_participante_apto():
    certificados.validar_elegibilidade(SimpleNamespace(presente=True, horas_obtidas=4), EVENTO)


def test_garantir_vaga_com_banco(sessao):
    db = sessao
    evento = Evento(titulo="E", descricao="d", data_evento=date(2026, 12, 1), capacidade=1, carga_horaria=1)
    u = Usuario(nome="u", email="u@x.com", perfil="participante")
    db.add_all([evento, u])
    db.commit()
    inscricoes.garantir_vaga(db, evento)  # há vaga
    db.add(Inscricao(id_usuario=u.id_usuario, id_evento=evento.id_evento, status="Ativa"))
    db.commit()
    with pytest.raises(Conflito):
        inscricoes.garantir_vaga(db, evento)
