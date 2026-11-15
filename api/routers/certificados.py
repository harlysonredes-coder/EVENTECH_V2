from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from api.deps import exigir_administrador
from api.docs import ADMIN, R404, R409, R422
from core.database import get_db
from schemas import CertificadoEntrada, CertificadoResposta, MensagemResposta
from services import certificados

router = APIRouter(
    prefix="/certificados", tags=["Certificados"], dependencies=[Depends(exigir_administrador)],
)


@router.post("", status_code=201, response_model=CertificadoResposta, summary="Emitir certificado (admin)",
             description="Exige presença confirmada e horas obtidas >= carga horária do evento (422). "
                         "Um certificado por participação (409).",
             responses={**ADMIN, **R404, **R409, **R422})
def emitir_certificado(dados: CertificadoEntrada, db: Session = Depends(get_db)):
    return certificados.emitir(db, dados)


@router.get("", response_model=list[CertificadoResposta], summary="Listar certificados (admin)", responses=ADMIN)
def listar_certificados(db: Session = Depends(get_db)):
    return db.query(models.Certificado).all()


@router.get("/{id_certificado}", response_model=CertificadoResposta, summary="Buscar certificado (admin)",
            responses={**ADMIN, **R404})
def buscar_certificado(id_certificado: int, db: Session = Depends(get_db)):
    return certificados.obter(db, id_certificado)


@router.put("/{id_certificado}", response_model=CertificadoResposta, summary="Atualizar certificado (admin)",
            responses={**ADMIN, **R404, **R409, **R422})
def atualizar_certificado(id_certificado: int, dados: CertificadoEntrada, db: Session = Depends(get_db)):
    return certificados.atualizar(db, id_certificado, dados)


@router.delete("/{id_certificado}", response_model=MensagemResposta, summary="Excluir certificado (admin)",
               responses={**ADMIN, **R404})
def excluir_certificado(id_certificado: int, db: Session = Depends(get_db)):
    certificados.excluir(db, id_certificado)
    return MensagemResposta(mensagem="Certificado excluído com sucesso")
