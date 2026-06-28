from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.staff import Staff, Compenso
from app.schemas.staff import StaffCreate, StaffRead, CompensoCreate, CompensoRead
from typing import List

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

# ---- COMPENSI ----

@router.get("/staff/{staff_id}/compensi", response_model=List[CompensoRead])
def lista_compensi(staff_id: int, db: Session = Depends(get_db)):
    return db.query(Compenso).filter(Compenso.staff_id == staff_id).all()

@router.post("/compensi/", response_model=CompensoRead)
def registra_compenso(compenso: CompensoCreate, db: Session = Depends(get_db)):
    compensi_precedenti = db.query(Compenso).filter(
        Compenso.staff_id == compenso.staff_id
    ).all()
    totale = sum(c.importo for c in compensi_precedenti) + compenso.importo
    soglia_superata = totale >= 5000
    db_compenso = Compenso(
        **compenso.model_dump(),
        totale_progressivo=totale,
        soglia_superata=soglia_superata
    )
    db.add(db_compenso)
    db.commit()
    db.refresh(db_compenso)
    return db_compenso
