from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.presenze import Evento, Presenza
from app.schemas.presenze import EventoCreate, EventoRead, EventoUpdate, PresenzaCreate, PresenzaRead
from typing import List

router = APIRouter(tags=["Presenze"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- EVENTI ----

@router.get("/eventi/", response_model=List[EventoRead])
def lista_eventi(db: Session = Depends(get_db)):
    return db.query(Evento).all()

@router.get("/eventi/{evento_id}", response_model=EventoRead)
def get_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return evento

@router.post("/eventi/", response_model=EventoRead)
def crea_evento(evento: EventoCreate, db: Session = Depends(get_db)):
    db_evento = Evento(**evento.model_dump())
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento

@router.put("/eventi/{evento_id}", response_model=EventoRead)
def modifica_evento(evento_id: int, dati: EventoUpdate, db: Session = Depends(get_db)):
    """Modifica i campi di un singolo evento (occorrenza). Non tocca le altre occorrenze
    della stessa serie ricorrente, anche se l'evento ne fa parte."""
    db_evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    for key, value in dati.model_dump(exclude_unset=True).items():
        setattr(db_evento, key, value)
    db.commit()
    db.refresh(db_evento)
    return db_evento

@router.delete("/eventi/{evento_id}")
def elimina_evento(evento_id: int, db: Session = Depends(get_db)):
    db_evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    db.delete(db_evento)
    db.commit()
    return {"messaggio": "Evento eliminato"}

# ---- PRESENZE ----

@router.get("/eventi/{evento_id}/presenze", response_model=List[PresenzaRead])
def lista_presenze_evento(evento_id: int, db: Session = Depends(get_db)):
    return db.query(Presenza).filter(Presenza.evento_id == evento_id).all()

@router.get("/tesserati/{tesserato_id}/presenze", response_model=List[PresenzaRead])
def lista_presenze_tesserato(tesserato_id: int, db: Session = Depends(get_db)):
    return db.query(Presenza).filter(Presenza.tesserato_id == tesserato_id).all()

@router.post("/presenze/", response_model=PresenzaRead)
def registra_presenza(presenza: PresenzaCreate, db: Session = Depends(get_db)):
    """Upsert: se esiste già una presenza per questo (evento, tesserato) la aggiorna
    invece di crearne una nuova. Evita i duplicati che rendevano la scelta
    dell'utente non più modificabile."""
    db_presenza = db.query(Presenza).filter(
        Presenza.evento_id == presenza.evento_id,
        Presenza.tesserato_id == presenza.tesserato_id,
    ).first()
    if db_presenza:
        for key, value in presenza.model_dump().items():
            setattr(db_presenza, key, value)
    else:
        db_presenza = Presenza(**presenza.model_dump())
        db.add(db_presenza)
    db.commit()
    db.refresh(db_presenza)
    return db_presenza

@router.put("/presenze/{presenza_id}", response_model=PresenzaRead)
def aggiorna_presenza(presenza_id: int, presenza: PresenzaCreate, db: Session = Depends(get_db)):
    db_presenza = db.query(Presenza).filter(Presenza.id == presenza_id).first()
    if not db_presenza:
        raise HTTPException(status_code=404, detail="Presenza non trovata")
    for key, value in presenza.model_dump().items():
        setattr(db_presenza, key, value)
    db.commit()
    db.refresh(db_presenza)
    return db_presenza

@router.delete("/eventi/{evento_id}/presenze/{tesserato_id}")
def annulla_assenza(evento_id: int, tesserato_id: int, db: Session = Depends(get_db)):
    """Rimuove il record di presenza: il tesserato torna allo stato di default (presente)."""
    db_presenza = db.query(Presenza).filter(
        Presenza.evento_id == evento_id,
        Presenza.tesserato_id == tesserato_id,
    ).first()
    if not db_presenza:
        raise HTTPException(status_code=404, detail="Presenza non trovata")
    db.delete(db_presenza)
    db.commit()
    return {"messaggio": "Presenza rimossa, tesserato tornato presente di default"}
