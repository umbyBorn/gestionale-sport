from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models.utenti import Gruppo, GruppoTesserato
from app.schemas.gruppi import GruppoCreate, GruppoRead
from typing import List

router = APIRouter(prefix="/gruppi", tags=["Gruppi"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _con_conteggio(gruppi: List[Gruppo], db: Session) -> List[Gruppo]:
    conteggi = dict(
        db.query(GruppoTesserato.gruppo_id, func.count(GruppoTesserato.id))
        .group_by(GruppoTesserato.gruppo_id)
        .all()
    )
    for g in gruppi:
        g.num_tesserati = conteggi.get(g.id, 0)
    return gruppi

@router.get("/", response_model=List[GruppoRead])
def lista_gruppi(db: Session = Depends(get_db)):
    gruppi = db.query(Gruppo).filter(Gruppo.attivo == True).all()
    return _con_conteggio(gruppi, db)

@router.get("/{gruppo_id}", response_model=GruppoRead)
def get_gruppo(gruppo_id: int, db: Session = Depends(get_db)):
    gruppo = db.query(Gruppo).filter(Gruppo.id == gruppo_id).first()
    if not gruppo:
        raise HTTPException(status_code=404, detail="Gruppo non trovato")
    _con_conteggio([gruppo], db)
    return gruppo

@router.post("/", response_model=GruppoRead)
def crea_gruppo(gruppo: GruppoCreate, db: Session = Depends(get_db)):
    db_gruppo = Gruppo(**gruppo.model_dump())
    db.add(db_gruppo)
    db.commit()
    db.refresh(db_gruppo)
    return db_gruppo

@router.put("/{gruppo_id}", response_model=GruppoRead)
def aggiorna_gruppo(gruppo_id: int, gruppo: GruppoCreate, db: Session = Depends(get_db)):
    db_gruppo = db.query(Gruppo).filter(Gruppo.id == gruppo_id).first()
    if not db_gruppo:
        raise HTTPException(status_code=404, detail="Gruppo non trovato")
    for key, value in gruppo.model_dump().items():
        setattr(db_gruppo, key, value)
    db.commit()
    db.refresh(db_gruppo)
    return db_gruppo

@router.delete("/{gruppo_id}")
def elimina_gruppo(gruppo_id: int, db: Session = Depends(get_db)):
    db_gruppo = db.query(Gruppo).filter(Gruppo.id == gruppo_id).first()
    if not db_gruppo:
        raise HTTPException(status_code=404, detail="Gruppo non trovato")
    db_gruppo.attivo = False
    db.commit()
    return {"messaggio": "Gruppo disattivato"}
