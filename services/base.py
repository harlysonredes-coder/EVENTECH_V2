from sqlalchemy.orm import Session

from core.exceptions import NaoEncontrado


def buscar_ou_404(db: Session, modelo, pk: int, rotulo: str):
    """Busca por PK ou lança NaoEncontrado. `rotulo` já inclui a concordância (ex.: 'Inscrição não encontrada')."""
    obj = db.get(modelo, pk)
    if obj is None:
        raise NaoEncontrado(rotulo)
    return obj


def salvar(db: Session, obj):
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def remover(db: Session, obj) -> None:
    db.delete(obj)
    db.commit()
