from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.presenze import Evento, EventoRicorrente, TipoEventoEnum
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time, timedelta
import json

router = APIRouter(tags=["Calendario"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class EventoRicorrenteCreate(BaseModel):
    gruppo_id: int
    tipo: str = "allenamento"
    titolo: str
    ora_inizio: Optional[str] = None
    ora_fine: Optional[str] = None
    luogo: Optional[str] = None
    giorni_settimana: List[int]  # 0=lunedi, 1=martedi, ..., 6=domenica
    data_inizio: date
    data_fine: date

class EventoRicorrenteRead(BaseModel):
    id: int
    gruppo_id: int
    tipo: str
    titolo: str
    ora_inizio: Optional[str] = None
    luogo: Optional[str] = None
    giorni_settimana: str
    data_inizio: date
    data_fine: date
    attivo: bool
    num_occorrenze: int = 0

    class Config:
        from_attributes = True

@router.get("/eventi-ricorrenti/", response_model=List[EventoRicorrenteRead])
def lista_eventi_ricorrenti(db: Session = Depends(get_db)):
    ricorrenti = db.query(EventoRicorrente).filter(EventoRicorrente.attivo == True).all()
    result = []
    for r in ricorrenti:
        num = db.query(Evento).filter(Evento.ricorrente_id == r.id).count()
        item = EventoRicorrenteRead(
            id=r.id,
            gruppo_id=r.gruppo_id,
            tipo=r.tipo.value,
            titolo=r.titolo,
            ora_inizio=str(r.ora_inizio) if r.ora_inizio else None,
            luogo=r.luogo,
            giorni_settimana=r.giorni_settimana,
            data_inizio=r.data_inizio,
            data_fine=r.data_fine,
            attivo=r.attivo,
            num_occorrenze=num
        )
        result.append(item)
    return result

@router.post("/eventi-ricorrenti/")
def crea_evento_ricorrente(evento: EventoRicorrenteCreate, db: Session = Depends(get_db)):
    giorni_str = json.dumps(evento.giorni_settimana)

    ora_inizio = None
    ora_fine = None
    if evento.ora_inizio:
        parts = evento.ora_inizio.split(":")
        ora_inizio = time(int(parts[0]), int(parts[1]))
    if evento.ora_fine:
        parts = evento.ora_fine.split(":")
        ora_fine = time(int(parts[0]), int(parts[1]))

    ricorrente = EventoRicorrente(
        gruppo_id=evento.gruppo_id,
        tipo=TipoEventoEnum(evento.tipo),
        titolo=evento.titolo,
        ora_inizio=ora_inizio,
        ora_fine=ora_fine,
        luogo=evento.luogo,
        giorni_settimana=giorni_str,
        data_inizio=evento.data_inizio,
        data_fine=evento.data_fine,
    )
    db.add(ricorrente)
    db.flush()

    # Genera le occorrenze
    giorni = json.loads(giorni_str)
    data_corrente = evento.data_inizio
    occorrenze_create = 0

    while data_corrente <= evento.data_fine:
        if data_corrente.weekday() in giorni:
            ev = Evento(
                gruppo_id=evento.gruppo_id,
                tipo=TipoEventoEnum(evento.tipo),
                titolo=evento.titolo,
                data=data_corrente,
                ora_inizio=ora_inizio,
                ora_fine=ora_fine,
                luogo=evento.luogo,
                ricorrente_id=ricorrente.id
            )
            db.add(ev)
            occorrenze_create += 1
        data_corrente += timedelta(days=1)

    db.commit()
    return {"messaggio": f"Evento ricorrente creato con {occorrenze_create} occorrenze"}

@router.delete("/eventi-ricorrenti/{ricorrente_id}")
def elimina_evento_ricorrente(ricorrente_id: int, elimina_futuri: bool = True, db: Session = Depends(get_db)):
    ricorrente = db.query(EventoRicorrente).filter(EventoRicorrente.id == ricorrente_id).first()
    if not ricorrente:
        raise HTTPException(status_code=404, detail="Evento ricorrente non trovato")
    ricorrente.attivo = False
    if elimina_futuri:
        oggi = date.today()
        eventi_futuri = db.query(Evento).filter(
            Evento.ricorrente_id == ricorrente_id,
            Evento.data >= oggi
        ).all()
        for e in eventi_futuri:
            db.delete(e)
    db.commit()
    return {"messaggio": "Evento ricorrente disattivato"}

@router.delete("/eventi/{evento_id}/occorrenza")
def elimina_occorrenza(evento_id: int, db: Session = Depends(get_db)):
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    db.delete(evento)
    db.commit()
    return {"messaggio": "Occorrenza eliminata"}

@router.get("/calendario/")
def get_calendario(anno: int, mese: int, db: Session = Depends(get_db)):
    from calendar import monthrange
    giorni_nel_mese = monthrange(anno, mese)[1]
    data_inizio = date(anno, mese, 1)
    data_fine = date(anno, mese, giorni_nel_mese)

    eventi = db.query(Evento).filter(
        Evento.data >= data_inizio,
        Evento.data <= data_fine
    ).all()

    risultato = {}
    for e in eventi:
        giorno = str(e.data)
        if giorno not in risultato:
            risultato[giorno] = []
        risultato[giorno].append({
            "id": e.id,
            "titolo": e.titolo,
            "tipo": e.tipo.value,
            "gruppo_id": e.gruppo_id,
            "ora_inizio": str(e.ora_inizio) if e.ora_inizio else None,
            "luogo": e.luogo,
            "ricorrente_id": e.ricorrente_id
        })

    return risultato
