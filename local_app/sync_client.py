"""Sincronizzazione tra il database locale (SQLite, offline) e il database
online (Neon), per un solo amministratore alla volta.

Uso tipico da dentro l'app locale (chiamato dal pulsante "Sincronizza"
esposto tramite un piccolo endpoint locale, vedi avvia_locale.py):

    from local_app.sync_client import ClienteSync
    cliente = ClienteSync(base_url_online="https://gestionale-sport-api.onrender.com",
                           token="...")
    cliente.clona_da_zero()      # solo al primo avvio, DB locale vuoto
    cliente.sincronizza()        # push + pull, da usare ogni volta che torna la rete
"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple, List

import requests
from sqlalchemy import create_engine, select, update as sa_update, delete as sa_delete, insert as sa_insert

from local_app.percorsi import percorso_db_locale, percorso_stato_sync


class ClienteSync:
    def __init__(self, base_url_online: str, token: str):
        self.base_url = base_url_online.rstrip("/")
        self.token = token
        self.engine = create_engine(f"sqlite:///{percorso_db_locale()}")

        # Import qui (non in cima al file) per essere sicuri che i modelli
        # siano già stati registrati sui metadata da avvia_locale.py
        from app.database import Base
        from app.sync.core import tabella_valida, coerce_valori, rimappa_fk
        self.Base = Base
        self._tabella_valida = tabella_valida
        self._coerce_valori = coerce_valori
        self._rimappa_fk = rimappa_fk

    # ---------------------------------------------------------------- stato
    def _leggi_stato(self) -> dict:
        p = percorso_stato_sync()
        if p.exists():
            return json.loads(p.read_text())
        return {"clonato": False, "ultimo_pull": None}

    def _scrivi_stato(self, stato: dict):
        percorso_stato_sync().write_text(json.dumps(stato, indent=2))

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    # --------------------------------------------------------- primo avvio
    def clona_da_zero(self):
        """Scarica TUTTO il contenuto attuale del database online e popola
        da zero il database locale. Da usare una sola volta, al primissimo
        avvio dell'app locale (o se si vuole ripartire da capo)."""
        r = requests.get(f"{self.base_url}/sync/clone", headers=self._headers(), timeout=120)
        r.raise_for_status()
        dati = r.json()

        with self.engine.begin() as conn:
            for nome_tabella, righe in dati["tabelle"].items():
                tabella = self.Base.metadata.tables.get(nome_tabella)
                if tabella is None or not righe:
                    continue
                conn.execute(sa_delete(tabella))
                for riga in righe:
                    riga = self._coerce_valori(tabella, dict(riga))
                    conn.execute(sa_insert(tabella).values(**riga))

        self._scrivi_stato({"clonato": True, "ultimo_pull": dati["timestamp_server"]})
        return {"tabelle_popolate": len(dati["tabelle"])}

    # --------------------------------------------------- raccolta modifiche
    def _voci_da_sincronizzare(self) -> List[dict]:
        with self.engine.connect() as conn:
            sync_log = self.Base.metadata.tables["sync_log"]
            righe = conn.execute(
                select(sync_log).where(
                    sync_log.c.sincronizzato.is_(False),
                    sync_log.c.origine == "locale",
                ).order_by(sync_log.c.timestamp.asc())
            ).mappings().all()
        return [dict(r) for r in righe]

    # ------------------------------------------------------------- sincro
    def sincronizza(self) -> dict:
        stato = self._leggi_stato()
        if not stato.get("clonato"):
            raise RuntimeError("Il database locale non è mai stato inizializzato: chiamare prima clona_da_zero()")

        risultato = {"inviate": 0, "ricevute": 0, "errori": []}

        # 1) PUSH: invio le modifiche fatte offline
        voci_locali = self._voci_da_sincronizzare()
        if voci_locali:
            corpo = {
                "voci": [
                    {
                        "tabella": v["tabella"],
                        "record_id": v["record_id"],
                        "operazione": v["operazione"],
                        "payload": json.loads(v["payload"]) if v["payload"] else None,
                        "timestamp": v["timestamp"].isoformat() if hasattr(v["timestamp"], "isoformat") else v["timestamp"],
                    }
                    for v in voci_locali
                ]
            }
            r = requests.post(f"{self.base_url}/sync/push", json=corpo, headers=self._headers(), timeout=120)
            r.raise_for_status()
            esito = r.json()
            risultato["inviate"] = esito["applicate"]
            risultato["errori"].extend(esito.get("errori", []))

            mappa_id: Dict[Tuple[str, int], int] = {
                (m["tabella"], m["id_locale"]): m["id_reale"] for m in esito.get("mappa_id", [])
            }
            self._applica_rimappatura_locale(mappa_id)

            with self.engine.begin() as conn:
                sync_log = self.Base.metadata.tables["sync_log"]
                ids = [v["id"] for v in voci_locali]
                conn.execute(
                    sa_update(sync_log).where(sync_log.c.id.in_(ids)).values(sincronizzato=True)
                )

        # 2) PULL: scarico le modifiche fatte online nel frattempo
        dal_timestamp = stato.get("ultimo_pull") or "1970-01-01T00:00:00Z"
        r = requests.get(
            f"{self.base_url}/sync/pull",
            params={"dal_timestamp": dal_timestamp},
            headers=self._headers(),
            timeout=120,
        )
        r.raise_for_status()
        esito_pull = r.json()

        with self.engine.begin() as conn:
            for voce in esito_pull["voci"]:
                tabella = self._tabella_valida(voce["tabella"])
                if tabella is None:
                    continue
                dati = self._coerce_valori(tabella, dict(voce["payload"] or {}))
                if voce["operazione"] in ("insert", "update"):
                    esistente = conn.execute(
                        select(tabella.c.id).where(tabella.c.id == voce["record_id"])
                    ).first()
                    if esistente:
                        conn.execute(sa_update(tabella).where(tabella.c.id == voce["record_id"]).values(**dati))
                    else:
                        conn.execute(sa_insert(tabella).values(**dati))
                elif voce["operazione"] == "delete":
                    conn.execute(sa_delete(tabella).where(tabella.c.id == voce["record_id"]))

        risultato["ricevute"] = len(esito_pull["voci"])
        self._scrivi_stato({"clonato": True, "ultimo_pull": esito_pull["timestamp_server"]})

        return risultato

    # ------------------------------------------------- rimappatura locale
    def _applica_rimappatura_locale(self, mappa_id: Dict[Tuple[str, int], int]):
        """Dopo un push, gli id negativi temporanei diventano id reali. Devo
        aggiornare sia la riga stessa (id primario) sia ogni colonna FK, in
        qualunque altra tabella, che puntava a quell'id temporaneo."""
        if not mappa_id:
            return
        with self.engine.begin() as conn:
            for (nome_tabella, id_locale), id_reale in mappa_id.items():
                tabella = self.Base.metadata.tables.get(nome_tabella)
                if tabella is None:
                    continue
                conn.execute(sa_update(tabella).where(tabella.c.id == id_locale).values(id=id_reale))

                # aggiorno le FK di tutte le altre tabelle che puntano a questo id
                for altra_tabella in self.Base.metadata.tables.values():
                    for col in altra_tabella.columns:
                        for fk in col.foreign_keys:
                            if fk.column.table.name == nome_tabella:
                                conn.execute(
                                    sa_update(altra_tabella)
                                    .where(col == id_locale)
                                    .values(**{col.name: id_reale})
                                )
