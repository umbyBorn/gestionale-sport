from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.presenze import Evento, EventoRicorrente, TipoEventoEnum, Presenza
from app.models.contabilita import Pagamento
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

class EventoRicorrenteUpdate(BaseModel):
    titolo: Optional[str] = None
    ora_inizio: Optional[str] = None
    ora_fine: Optional[str] = None
    luogo: Optional[str] = None
    solo_futuri: bool = True

@router.put("/eventi-ricorrenti/{ricorrente_id}")
def modifica_evento_ricorrente(ricorrente_id: int, dati: EventoRicorrenteUpdate, db: Session = Depends(get_db)):
    """Applica le modifiche a tutte le occorrenze (future, o anche passate se solo_futuri=False)."""
    ricorrente = db.query(EventoRicorrente).filter(EventoRicorrente.id == ricorrente_id).first()
    if not ricorrente:
        raise HTTPException(status_code=404, detail="Evento ricorrente non trovato")

    ora_inizio = None
    ora_fine = None
    if dati.ora_inizio:
        parts = dati.ora_inizio.split(":")
        ora_inizio = time(int(parts[0]), int(parts[1]))
    if dati.ora_fine:
        parts = dati.ora_fine.split(":")
        ora_fine = time(int(parts[0]), int(parts[1]))

    if dati.titolo:
        ricorrente.titolo = dati.titolo
    if dati.ora_inizio:
        ricorrente.ora_inizio = ora_inizio
    if dati.ora_fine:
        ricorrente.ora_fine = ora_fine
    if dati.luogo is not None:
        ricorrente.luogo = dati.luogo

    q = db.query(Evento).filter(Evento.ricorrente_id == ricorrente_id)
    if dati.solo_futuri:
        q = q.filter(Evento.data >= date.today())
    occorrenze = q.all()
    for e in occorrenze:
        if dati.titolo:
            e.titolo = dati.titolo
        if dati.ora_inizio:
            e.ora_inizio = ora_inizio
        if dati.ora_fine:
            e.ora_fine = ora_fine
        if dati.luogo is not None:
            e.luogo = dati.luogo

    db.commit()
    return {"messaggio": f"Aggiornate {len(occorrenze)} occorrenze"}

def _elimina_evento_sicuro(db: Session, evento: Evento, forza_con_presenze: bool = False):
    """Elimina un evento gestendo le dipendenze.
    Se l'evento ha già presenze registrate e forza_con_presenze=False, NON lo elimina
    (viene saltato) per evitare di perdere dati senza che l'utente lo sappia.
    Restituisce True se l'evento è stato eliminato, False se è stato saltato."""
    ha_presenze = db.query(Presenza).filter(Presenza.evento_id == evento.id).first() is not None
    if ha_presenze and not forza_con_presenze:
        return False
    db.query(Presenza).filter(Presenza.evento_id == evento.id).delete(synchronize_session=False)
    db.query(Pagamento).filter(Pagamento.evento_id == evento.id).update(
        {Pagamento.evento_id: None}, synchronize_session=False
    )
    db.delete(evento)
    return True


@router.delete("/eventi-ricorrenti/{ricorrente_id}")
def elimina_evento_ricorrente(
    ricorrente_id: int,
    elimina_futuri: bool = True,
    forza_con_presenze: bool = False,
    db: Session = Depends(get_db),
):
    ricorrente = db.query(EventoRicorrente).filter(EventoRicorrente.id == ricorrente_id).first()
    if not ricorrente:
        raise HTTPException(status_code=404, detail="Evento ricorrente non trovato")
    ricorrente.attivo = False
    eliminati = 0
    saltati_con_presenze = 0
    totale_serie = db.query(Evento).filter(Evento.ricorrente_id == ricorrente_id).count()
    if elimina_futuri:
        oggi = date.today()
        eventi_futuri = db.query(Evento).filter(
            Evento.ricorrente_id == ricorrente_id,
            Evento.data >= oggi
        ).all()
        for e in eventi_futuri:
            if _elimina_evento_sicuro(db, e, forza_con_presenze):
                eliminati += 1
            else:
                saltati_con_presenze += 1
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Impossibile eliminare la serie: {str(exc)}")
    return {
        "messaggio": "Evento ricorrente disattivato",
        "occorrenze_eliminate": eliminati,
        "saltate_con_presenze": saltati_con_presenze,
        "totale_eventi_nella_serie_prima_dell_eliminazione": totale_serie,
    }

@router.delete("/eventi/{evento_id}/occorrenza")
def elimina_occorrenza(evento_id: int, forza_con_presenze: bool = False, db: Session = Depends(get_db)):
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    eliminato = _elimina_evento_sicuro(db, evento, forza_con_presenze)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Impossibile eliminare l'evento: {str(exc)}")
    if not eliminato:
        return {"messaggio": "Evento non eliminato: ha già presenze registrate", "eliminato": False}
    return {"messaggio": "Occorrenza eliminata", "eliminato": True}

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
