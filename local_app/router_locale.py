"""Endpoint esposti SOLO dall'app locale (mai online su Render) per gestire
la configurazione della connessione al sistema online e la sincronizzazione.
Il frontend, quando gira in modalità locale, mostra un pulsante
"Sincronizza" che chiama /locale/sincronizza."""
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests

from local_app.percorsi import percorso_stato_sync
from local_app.sync_client import ClienteSync

router = APIRouter(prefix="/locale", tags=["App locale"])


class ConfiguraRichiesta(BaseModel):
    base_url_online: str
    email: str
    password: str


def _leggi_stato() -> dict:
    p = percorso_stato_sync()
    if p.exists():
        return json.loads(p.read_text())
    return {"clonato": False, "ultimo_pull": None}


def _scrivi_stato(stato: dict):
    percorso_stato_sync().write_text(json.dumps(stato, indent=2))


@router.get("/stato")
def stato():
    s = _leggi_stato()
    return {
        "clonato": s.get("clonato", False),
        "ultimo_pull": s.get("ultimo_pull"),
        "base_url_online": s.get("base_url_online"),
        "configurato": bool(s.get("token")),
    }


@router.post("/configura")
def configura(dati: ConfiguraRichiesta):
    """Login sul sistema online per ottenere il token, salvato poi in
    locale per le successive sincronizzazioni (finché non si rifà login)."""
    try:
        r = requests.post(
            f"{dati.base_url_online.rstrip('/')}/auth/login",
            data={"username": dati.email, "password": dati.password},
            timeout=15,
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Impossibile raggiungere il server online: {e}")

    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Credenziali non valide sul sistema online")

    token = r.json()["access_token"]
    stato = _leggi_stato()
    stato["token"] = token
    stato["base_url_online"] = dati.base_url_online.rstrip("/")
    _scrivi_stato(stato)
    return {"messaggio": "Connessione configurata correttamente"}


@router.post("/clona")
def clona():
    stato = _leggi_stato()
    if not stato.get("token"):
        raise HTTPException(status_code=400, detail="Configura prima la connessione (login online)")
    try:
        cliente = ClienteSync(stato["base_url_online"], stato["token"])
        esito = cliente.clona_da_zero()
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Errore di rete durante la clonazione: {e}")
    return esito


@router.post("/sincronizza")
def sincronizza():
    stato = _leggi_stato()
    if not stato.get("token"):
        raise HTTPException(status_code=400, detail="Configura prima la connessione (login online)")
    if not stato.get("clonato"):
        raise HTTPException(status_code=400, detail="Esegui prima la clonazione iniziale")
    try:
        cliente = ClienteSync(stato["base_url_online"], stato["token"])
        esito = cliente.sincronizza()
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Nessuna connessione di rete disponibile: {e}")
    return esito
