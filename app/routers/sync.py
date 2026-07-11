"""Endpoint di sincronizzazione tra l'app locale (offline, SQLite) e il
database online (Neon), pensati per un solo amministratore alla volta
(nessuna gestione di conflitti multi-utente).

Logica:
- PUSH: la app locale invia le voci di sync_log accumulate mentre era
  offline. Il server le applica sul database online in ordine cronologico.
  I record creati offline arrivano con un id NEGATIVO (placeholder locale);
  il server li inserisce lasciando che sia il DB online ad assegnare il vero
  id, e restituisce la mappa id_locale -> id_reale così la app locale può
  aggiornare i propri riferimenti (comprese le chiavi esterne).
- PULL: la app locale chiede "cosa è cambiato online da questo timestamp in
  poi", per scaricare le modifiche fatte direttamente sul sistema online
  (es. iscrizioni pubbliche, RSVP dei tesserati) mentre l'amministratore
  era offline.
"""
from datetime import datetime, timezone
from typing import Dict, Tuple, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, update as sa_update, delete as sa_delete

from app.database import SessionLocal, Base
from app.models.sync import SyncLog
from app.models.utenti import Utente
from app.auth import richiedi_ruolo
from app.schemas.sync import PushRequest, PushResponse, MappaId, PullResponse
from app.sync.core import tabella_valida as _tabella_valida, coerce_valori as _coerce_valori, rimappa_fk as _rimappa_fk

router = APIRouter(prefix="/sync", tags=["Sincronizzazione"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/clone")
def clone_completo(
    db: Session = Depends(get_db),
    utente: Utente = Depends(richiedi_ruolo("amministratore")),
):
    """Restituisce il contenuto COMPLETO e ATTUALE di tutte le tabelle
    (esclusa sync_log). Usato una sola volta, al primo avvio dell'app
    locale, per popolare il database SQLite di partenza con tutto lo
    storico già esistente (che sync_log non contiene, dato che registra
    solo le modifiche fatte da quando questa funzione è stata introdotta)."""
    import json as _json
    from datetime import datetime as _dt, date as _date, time as _time
    import decimal, enum as _enum

    def serializza(v):
        if isinstance(v, (_dt, _date, _time)):
            return v.isoformat()
        if isinstance(v, decimal.Decimal):
            return float(v)
        if isinstance(v, _enum.Enum):
            return v.value
        if isinstance(v, (bytes, bytearray)):
            return None
        return v

    risultato = {}
    for nome_tabella, tabella in Base.metadata.tables.items():
        if nome_tabella == "sync_log":
            continue
        righe = db.execute(tabella.select()).mappings().all()
        risultato[nome_tabella] = [
            {k: serializza(v) for k, v in dict(r).items()} for r in righe
        ]
    return {"timestamp_server": datetime.now(timezone.utc).isoformat(), "tabelle": risultato}


@router.post("/push", response_model=PushResponse)
def push(
    richiesta: PushRequest,
    db: Session = Depends(get_db),
    utente: Utente = Depends(richiedi_ruolo("amministratore")),
):
    errori = []
    mappa_id: Dict[Tuple[str, int], int] = {}
    applicate = 0

    voci_ordinate = sorted(
        richiesta.voci,
        key=lambda v: v.timestamp or datetime.min.replace(tzinfo=timezone.utc)
    )

    for voce in voci_ordinate:
        tabella = _tabella_valida(voce.tabella)
        if tabella is None:
            errori.append(f"Tabella sconosciuta: {voce.tabella}")
            continue

        try:
            if voce.operazione == "insert":
                dati = dict(voce.payload or {})
                dati = _coerce_valori(tabella, dati)
                dati = _rimappa_fk(tabella, dati, mappa_id)
                id_locale = voce.record_id

                if id_locale < 0:
                    # Nuovo record creato offline: rimuovo l'id locale e lascio
                    # che sia il DB online ad assegnarne uno reale.
                    dati.pop("id", None)
                    risultato = db.execute(tabella.insert().values(**dati))
                    id_reale = risultato.inserted_primary_key[0]
                    mappa_id[(voce.tabella, id_locale)] = id_reale
                else:
                    # Record già con id reale (raro per un insert, ma gestito
                    # come upsert difensivo)
                    esistente = db.execute(
                        select(tabella.c.id).where(tabella.c.id == id_locale)
                    ).first()
                    if esistente:
                        db.execute(
                            sa_update(tabella).where(tabella.c.id == id_locale).values(**dati)
                        )
                    else:
                        db.execute(tabella.insert().values(**dati))

            elif voce.operazione == "update":
                dati = dict(voce.payload or {})
                dati = _coerce_valori(tabella, dati)
                dati = _rimappa_fk(tabella, dati, mappa_id)
                id_reale = mappa_id.get((voce.tabella, voce.record_id), voce.record_id)
                if id_reale < 0:
                    # Il record non è mai stato sincronizzato come insert in
                    # questo stesso push (caso limite): lo trattiamo come insert.
                    dati.pop("id", None)
                    risultato = db.execute(tabella.insert().values(**dati))
                    mappa_id[(voce.tabella, voce.record_id)] = risultato.inserted_primary_key[0]
                else:
                    db.execute(
                        sa_update(tabella).where(tabella.c.id == id_reale).values(**dati)
                    )

            elif voce.operazione == "delete":
                id_reale = mappa_id.get((voce.tabella, voce.record_id), voce.record_id)
                if id_reale > 0:
                    db.execute(sa_delete(tabella).where(tabella.c.id == id_reale))
                # se id_reale < 0: creato e cancellato offline prima di
                # qualunque sync, non è mai esistito online: nulla da fare

            applicate += 1
        except Exception as e:
            errori.append(f"{voce.tabella}#{voce.record_id} ({voce.operazione}): {e}")

    db.commit()

    return PushResponse(
        applicate=applicate,
        errori=errori,
        mappa_id=[MappaId(tabella=t, id_locale=i, id_reale=r) for (t, i), r in mappa_id.items()],
    )


@router.get("/pull", response_model=PullResponse)
def pull(
    dal_timestamp: datetime,
    db: Session = Depends(get_db),
    utente: Utente = Depends(richiedi_ruolo("amministratore")),
):
    """Restituisce tutte le modifiche fatte DIRETTAMENTE sul sistema online
    (portale pubblico, RSVP tesserati, altri operatori via web) dopo
    dal_timestamp, da applicare al database locale."""
    voci = (
        db.query(SyncLog)
        .filter(SyncLog.timestamp > dal_timestamp, SyncLog.origine == "online")
        .order_by(SyncLog.timestamp.asc())
        .all()
    )
    risultato = []
    for v in voci:
        import json
        risultato.append({
            "id": v.id,
            "tabella": v.tabella,
            "record_id": v.record_id,
            "operazione": v.operazione,
            "payload": json.loads(v.payload) if v.payload else None,
            "timestamp": v.timestamp,
        })
    return PullResponse(voci=risultato, timestamp_server=datetime.now(timezone.utc))
