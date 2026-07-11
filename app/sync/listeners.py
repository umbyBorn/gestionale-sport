"""Registra automaticamente ogni modifica (insert/update/delete) fatta su
QUALSIASI modello SQLAlchemy dell'app dentro la tabella sync_log, senza
bisogno di toccare i singoli router/endpoint.

Basta importare questo modulo una volta all'avvio dell'app (vedi app/main.py)
perché i listener restino attivi per tutta la durata del processo.
"""
import os
import json
import datetime
import decimal
import enum

from sqlalchemy import event
from sqlalchemy.orm import Mapper

from app.models.sync import SyncLog

# Tabelle da NON tracciare (la tabella di log stessa, per evitare ricorsione infinita)
TABELLE_ESCLUSE = {"sync_log"}

# 'locale' quando l'app gira come app desktop offline sul PC dell'amministratore,
# 'online' quando gira su Render collegata a Neon. Impostata tramite variabile
# d'ambiente APP_MODE (default: online).
ORIGINE = os.getenv("APP_MODE", "online")


def _serializza_valore(v):
    if isinstance(v, (datetime.datetime, datetime.date, datetime.time)):
        return v.isoformat()
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, enum.Enum):
        return v.value
    if isinstance(v, (bytes, bytearray)):
        return None
    return v


def _riga_a_dict(target) -> dict:
    mapper = target.__mapper__
    return {c.key: _serializza_valore(getattr(target, c.key)) for c in mapper.column_attrs}


def _registra(connection, target, operazione: str):
    tabella = getattr(target, "__tablename__", None)
    if not tabella or tabella in TABELLE_ESCLUSE:
        return
    record_id = getattr(target, "id", None)
    if record_id is None:
        return

    payload = None
    if operazione != "delete":
        try:
            payload = json.dumps(_riga_a_dict(target))
        except Exception:
            payload = None

    connection.execute(
        SyncLog.__table__.insert().values(
            tabella=tabella,
            record_id=record_id,
            operazione=operazione,
            payload=payload,
            sincronizzato=False,
            origine=ORIGINE,
        )
    )


@event.listens_for(Mapper, "after_insert")
def _log_insert(mapper, connection, target):
    _registra(connection, target, "insert")


@event.listens_for(Mapper, "after_update")
def _log_update(mapper, connection, target):
    _registra(connection, target, "update")


@event.listens_for(Mapper, "after_delete")
def _log_delete(mapper, connection, target):
    _registra(connection, target, "delete")
