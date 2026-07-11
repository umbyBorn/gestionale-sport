"""Funzioni generiche per applicare voci di sync_log a un database (online o
locale), condivise tra app/routers/sync.py (lato server) e
local_app/sync_client.py (lato app locale offline)."""
from datetime import datetime, date, time
from typing import Dict, Tuple

from sqlalchemy import Date, DateTime, Time
from app.database import Base

TABELLE_ESCLUSE = {"sync_log"}


def tabella_valida(nome: str):
    return Base.metadata.tables.get(nome) if nome not in TABELLE_ESCLUSE else None


def coerce_valori(tabella, dati: dict) -> dict:
    """Converte le stringhe ISO (arrivate da JSON) negli oggetti Python
    date/datetime/time attesi dalla colonna."""
    for col in tabella.columns:
        if col.name not in dati or dati[col.name] is None:
            continue
        valore = dati[col.name]
        if not isinstance(valore, str):
            continue
        try:
            if isinstance(col.type, DateTime):
                dati[col.name] = datetime.fromisoformat(valore)
            elif isinstance(col.type, Date):
                dati[col.name] = date.fromisoformat(valore[:10])
            elif isinstance(col.type, Time):
                dati[col.name] = time.fromisoformat(valore)
        except ValueError:
            pass
    return dati


def rimappa_fk(tabella, dati: dict, mappa_id: Dict[Tuple[str, int], int]) -> dict:
    """Sostituisce, nei valori delle colonne FK, un id locale negativo con
    il corrispondente id reale già assegnato in questa stessa sessione di
    sincronizzazione (se già processato)."""
    for col in tabella.columns:
        for fk in col.foreign_keys:
            tabella_riferita = fk.column.table.name
            valore = dati.get(col.name)
            if isinstance(valore, int) and valore < 0:
                reale = mappa_id.get((tabella_riferita, valore))
                if reale is not None:
                    dati[col.name] = reale
    return dati
