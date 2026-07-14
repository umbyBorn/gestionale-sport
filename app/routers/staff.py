from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.staff import Staff, Compenso, Contratto, StaffGruppo
from app.models.utenti import Gruppo
from app.schemas.staff import (
    StaffCreate, StaffRead, CompensoCreate, CompensoRead,
    ContrattoCreate, ContrattoRead,
)
from typing import List
from pydantic import BaseModel

router = APIRouter(tags=["Staff"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- STAFF ----

@router.get("/staff/", response_model=List[StaffRead])
def lista_staff(db: Session = Depends(get_db)):
    return db.query(Staff).filter(Staff.attivo == True).all()

@router.get("/staff/{staff_id}", response_model=StaffRead)
def get_staff(staff_id: int, db: Session = Depends(get_db)):
    membro = db.query(Staff).filter(Staff.id == staff_id).first()
    if not membro:
        raise HTTPException(status_code=404, detail="Membro staff non trovato")
    return membro

@router.post("/staff/", response_model=StaffRead)
def crea_staff(membro: StaffCreate, db: Session = Depends(get_db)):
    db_membro = Staff(**membro.model_dump())
    db.add(db_membro)
    db.commit()
    db.refresh(db_membro)
    return db_membro

@router.put("/staff/{staff_id}", response_model=StaffRead)
def aggiorna_staff(staff_id: int, membro: StaffCreate, db: Session = Depends(get_db)):
    db_membro = db.query(Staff).filter(Staff.id == staff_id).first()
    if not db_membro:
        raise HTTPException(status_code=404, detail="Membro staff non trovato")
    for key, value in membro.model_dump().items():
        setattr(db_membro, key, value)
    db.commit()
    db.refresh(db_membro)
    return db_membro

@router.delete("/staff/{staff_id}")
def elimina_staff(staff_id: int, db: Session = Depends(get_db)):
    db_membro = db.query(Staff).filter(Staff.id == staff_id).first()
    if not db_membro:
        raise HTTPException(status_code=404, detail="Membro staff non trovato")
    db_membro.attivo = False
    db.commit()
    return {"messaggio": "Membro staff disattivato"}


# ---- GRUPPI ASSEGNATI ALLO STAFF ----

class GruppiStaffUpdate(BaseModel):
    gruppo_ids: List[int]

@router.get("/staff/{staff_id}/gruppi")
def gruppi_staff(staff_id: int, db: Session = Depends(get_db)):
    righe = db.query(StaffGruppo).filter(StaffGruppo.staff_id == staff_id).all()
    gruppo_ids = [r.gruppo_id for r in righe]
    return db.query(Gruppo).filter(Gruppo.id.in_(gruppo_ids)).all() if gruppo_ids else []

@router.put("/staff/{staff_id}/gruppi")
def aggiorna_gruppi_staff(staff_id: int, dati: GruppiStaffUpdate, db: Session = Depends(get_db)):
    for riga in db.query(StaffGruppo).filter(StaffGruppo.staff_id == staff_id).all():
        db.delete(riga)
    for gid in dati.gruppo_ids:
        db.add(StaffGruppo(staff_id=staff_id, gruppo_id=gid))
    db.commit()
    return {"messaggio": "Gruppi aggiornati"}


# ---- COMPENSI ----

@router.get("/staff/{staff_id}/compensi", response_model=List[CompensoRead])
def lista_compensi(staff_id: int, db: Session = Depends(get_db)):
    return db.query(Compenso).filter(Compenso.staff_id == staff_id).order_by(Compenso.data_erogazione.desc()).all()

def _ricalcola_progressivi(db: Session, staff_id: int):
    """Ricalcola il totale progressivo e la soglia per tutti i compensi di un membro, in ordine cronologico."""
    compensi = db.query(Compenso).filter(Compenso.staff_id == staff_id).order_by(Compenso.data_erogazione).all()
    totale = 0.0
    for c in compensi:
        totale += float(c.importo)
        c.totale_progressivo = totale
        c.soglia_superata = totale >= 5000
    db.commit()

@router.post("/compensi/", response_model=CompensoRead)
def registra_compenso(compenso: CompensoCreate, db: Session = Depends(get_db)):
    db_compenso = Compenso(**compenso.model_dump(), totale_progressivo=0, soglia_superata=False)
    db.add(db_compenso)
    db.commit()
    _ricalcola_progressivi(db, compenso.staff_id)
    db.refresh(db_compenso)
    return db_compenso

@router.put("/compensi/{compenso_id}", response_model=CompensoRead)
def aggiorna_compenso(compenso_id: int, compenso: CompensoCreate, db: Session = Depends(get_db)):
    db_compenso = db.query(Compenso).filter(Compenso.id == compenso_id).first()
    if not db_compenso:
        raise HTTPException(status_code=404, detail="Compenso non trovato")
    for key, value in compenso.model_dump().items():
        setattr(db_compenso, key, value)
    db.commit()
    _ricalcola_progressivi(db, db_compenso.staff_id)
    db.refresh(db_compenso)
    return db_compenso

@router.delete("/compensi/{compenso_id}")
def elimina_compenso(compenso_id: int, db: Session = Depends(get_db)):
    db_compenso = db.query(Compenso).filter(Compenso.id == compenso_id).first()
    if not db_compenso:
        raise HTTPException(status_code=404, detail="Compenso non trovato")
    staff_id = db_compenso.staff_id
    db.delete(db_compenso)
    db.commit()
    _ricalcola_progressivi(db, staff_id)
    return {"messaggio": "Compenso eliminato"}


# ---- CONTRATTI ----

@router.get("/staff/{staff_id}/contratti", response_model=List[ContrattoRead])
def lista_contratti(staff_id: int, db: Session = Depends(get_db)):
    return db.query(Contratto).filter(Contratto.staff_id == staff_id).order_by(Contratto.data_inizio.desc()).all()

@router.post("/contratti/", response_model=ContrattoRead)
def crea_contratto(contratto: ContrattoCreate, db: Session = Depends(get_db)):
    db_contratto = Contratto(**contratto.model_dump())
    db.add(db_contratto)
    db.commit()
    db.refresh(db_contratto)
    return db_contratto

@router.put("/contratti/{contratto_id}", response_model=ContrattoRead)
def aggiorna_contratto(contratto_id: int, contratto: ContrattoCreate, db: Session = Depends(get_db)):
    db_contratto = db.query(Contratto).filter(Contratto.id == contratto_id).first()
    if not db_contratto:
        raise HTTPException(status_code=404, detail="Contratto non trovato")
    for key, value in contratto.model_dump().items():
        setattr(db_contratto, key, value)
    db.commit()
    db.refresh(db_contratto)
    return db_contratto

@router.delete("/contratti/{contratto_id}")
def elimina_contratto(contratto_id: int, db: Session = Depends(get_db)):
    db_contratto = db.query(Contratto).filter(Contratto.id == contratto_id).first()
    if not db_contratto:
        raise HTTPException(status_code=404, detail="Contratto non trovato")
    db.delete(db_contratto)
    db.commit()
    return {"messaggio": "Contratto eliminato"}

