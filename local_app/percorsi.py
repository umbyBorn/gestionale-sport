"""Percorsi usati dall'app locale: dove tenere il database SQLite, lo stato
di sincronizzazione e le eventuali code di file da caricare su Cloudinary
quando torna la rete."""
import os
from pathlib import Path


def cartella_dati() -> Path:
    """Restituisce (creandola se necessario) la cartella dati dell'app,
    tipicamente %APPDATA%/PGSJuvenilia su Windows, ~/.pgs_juvenilia altrove."""
    base = os.getenv("APPDATA")
    if base:
        cartella = Path(base) / "PGSJuvenilia"
    else:
        cartella = Path.home() / ".pgs_juvenilia"
    cartella.mkdir(parents=True, exist_ok=True)
    return cartella


def percorso_db_locale() -> Path:
    return cartella_dati() / "gestionale_locale.db"


def percorso_stato_sync() -> Path:
    return cartella_dati() / "stato_sync.json"


def cartella_upload_in_sospeso() -> Path:
    cartella = cartella_dati() / "upload_in_sospeso"
    cartella.mkdir(parents=True, exist_ok=True)
    return cartella
