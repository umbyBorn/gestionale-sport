from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.utenti import Tesserato
from app.schemas.tesserati import TesseratoCreate, TesseratoRead
from typing import List

router = APIRouter(prefix="/tesserati", tags=["Tesserati"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/tutti", response_model=List[TesseratoRead])
def lista_tutti_tesserati(db: Session = Depends(get_db)):
    return db.query(Tesserato).all()

@router.get("/", response_model=List[TesseratoRead])
def lista_tesserati(db: Session = Depends(get_db)):
    return db.query(Tesserato).filter(Tesserato.attivo == True).all()

@router.get("/{tesserato_id}", response_model=TesseratoRead)
def get_tesserato(tesserato_id: int, db: Session = Depends(get_db)):
    tesserato = db.query(Tesserato).filter(Tesserato.id == tesserato_id).first()
    if not tesserato:
        raise HTTPException(status_code=404, detail="Tesserato non trovato")
    return tesserato

@router.post("/", response_model=TesseratoRead)
def crea_tesserato(tesserato: TesseratoCreate, db: Session = Depends(get_db)):
    db_tesserato = Tesserato(**tesserato.model_dump())
    db.add(db_tesserato)
    db.commit()
    db.refresh(db_tesserato)
    return db_tesserato

@router.put("/{tesserato_id}", response_model=TesseratoRead)
def aggiorna_tesserato(tesserato_id: int, tesserato: TesseratoCreate, db: Session = Depends(get_db)):
    db_tesserato = db.query(Tesserato).filter(Tesserato.id == tesserato_id).first()
    if not db_tesserato:
        raise HTTPException(status_code=404, detail="Tesserato non trovato")
    for key, value in tesserato.model_dump().items():
        setattr(db_tesserato, key, value)
    db.commit()
    db.refresh(db_tesserato)
    return db_tesserato

@router.put("/{tesserato_id}/riattiva", response_model=TesseratoRead)
def riattiva_tesserato(tesserato_id: int, db: Session = Depends(get_db)):
    db_tesserato = db.query(Tesserato).filter(Tesserato.id == tesserato_id).first()
    if not db_tesserato:
        raise HTTPException(status_code=404, detail="Tesserato non trovato")
    db_tesserato.attivo = True
    db.commit()
    db.refresh(db_tesserato)
    return db_tesserato

@router.delete("/{tesserato_id}")
def elimina_tesserato(tesserato_id: int, db: Session = Depends(get_db)):
    db_tesserato = db.query(Tesserato).filter(Tesserato.id == tesserato_id).first()
    if not db_tesserato:
        raise HTTPException(status_code=404, detail="Tesserato non trovato")
    db_tesserato.attivo = False
    db.commit()
    return {"messaggio": "Tesserato disattivato"}
