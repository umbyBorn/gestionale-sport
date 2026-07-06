from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.utenti import RichiestaIscrizione, DatiRichiesta, Tesserato, Genitore
from app.auth import get_utente_corrente
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter(tags=["Iscrizioni"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ModuloCreate(BaseModel):
    nome_modulo: str


class DatiIscrizioneInput(BaseModel):
    nome: str
    cognome: str
    data_nascita: str
    codice_fiscale: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    cellulare: Optional[str] = None
    indirizzo: Optional[str] = None
    comune_residenza: Optional[str] = None
    provincia_residenza: Optional[str] = None
    cap_residenza: Optional[str] = None
    comune_nascita: Optional[str] = None
    provincia_nascita: Optional[str] = None
    stato_nascita: Optional[str] = None
    sesso: Optional[str] = None
    sport: Optional[str] = None
    genitore_nome: Optional[str] = None
    genitore_cognome: Optional[str] = None
    genitore_email: Optional[str] = None
    genitore_telefono: Optional[str] = None
    genitore_documento_tipo: Optional[str] = None
    genitore_documento_numero: Optional[str] = None
    consenso_privacy: bool = False
    note: Optional[str] = None


# ---- ADMIN: gestione moduli ----

@router.get("/iscrizioni/moduli")
def lista_moduli(db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    moduli = db.query(RichiestaIscrizione).all()
    result = []
    for m in moduli:
        n_richieste = db.query(DatiRichiesta).filter(DatiRichiesta.modulo_id == m.id).count()
        n_attesa = db.query(DatiRichiesta).filter(DatiRichiesta.modulo_id == m.id, DatiRichiesta.stato == "in_attesa").count()
        result.append({
            "id": m.id,
            "nome_modulo": m.nome_modulo,
            "token": m.token,
            "attivo": m.attivo,
            "link": f"/iscriviti/{m.token}",
            "n_richieste": n_richieste,
            "n_attesa": n_attesa,
            "created_at": m.created_at,
        })
    return result


@router.post("/iscrizioni/moduli")
def crea_modulo(dati: ModuloCreate, db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    token = uuid.uuid4().hex
    modulo = RichiestaIscrizione(
        token=token,
        nome_modulo=dati.nome_modulo,
        attivo=True,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    db.add(modulo)
    db.commit()
    db.refresh(modulo)
    return {"id": modulo.id, "token": token, "link": f"/iscriviti/{token}"}


@router.delete("/iscrizioni/moduli/{modulo_id}")
def elimina_modulo(modulo_id: int, db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    modulo = db.query(RichiestaIscrizione).filter(RichiestaIscrizione.id == modulo_id).first()
    if not modulo:
        raise HTTPException(status_code=404, detail="Modulo non trovato")
    modulo.attivo = False
    db.commit()
    return {"ok": True}


@router.get("/iscrizioni/richieste")
def lista_richieste(db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    richieste = db.query(DatiRichiesta).order_by(DatiRichiesta.id.desc()).all()
    return [{
        "id": r.id,
        "stato": r.stato,
        "nome": r.nome,
        "cognome": r.cognome,
        "data_nascita": r.data_nascita,
        "codice_fiscale": r.codice_fiscale,
        "email": r.email,
        "telefono": r.telefono,
        "cellulare": r.cellulare,
        "sesso": r.sesso,
        "sport": r.sport,
        "comune_nascita": r.comune_nascita,
        "provincia_nascita": r.provincia_nascita,
        "stato_nascita": r.stato_nascita,
        "indirizzo": r.indirizzo,
        "comune_residenza": r.comune_residenza,
        "provincia_residenza": r.provincia_residenza,
        "cap_residenza": r.cap_residenza,
        "genitore_nome": r.genitore_nome,
        "genitore_cognome": r.genitore_cognome,
        "genitore_email": r.genitore_email,
        "genitore_telefono": r.genitore_telefono,
        "genitore_documento_tipo": r.genitore_documento_tipo,
        "genitore_documento_numero": r.genitore_documento_numero,
        "consenso_privacy": r.consenso_privacy,
        "data_invio": r.data_invio,
        "note": r.note,
        "modulo_id": r.modulo_id,
    } for r in richieste]


@router.post("/iscrizioni/richieste/{richiesta_id}/approva")
def approva_richiesta(richiesta_id: int, db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    r = db.query(DatiRichiesta).filter(DatiRichiesta.id == richiesta_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Richiesta non trovata")

    # Crea genitore se presente
    genitore_id = None
    if r.genitore_nome and r.genitore_cognome:
        genitore = Genitore(
            nome=r.genitore_nome,
            cognome=r.genitore_cognome,
            email=r.genitore_email,
            telefono=r.genitore_telefono,
            documento_tipo=r.genitore_documento_tipo,
            documento_numero=r.genitore_documento_numero,
        )
        db.add(genitore)
        db.flush()
        genitore_id = genitore.id

    # Crea tesserato
    cf = r.codice_fiscale or f"TEMP_{uuid.uuid4().hex[:8].upper()}"
    tesserato = Tesserato(
        nome=r.nome,
        cognome=r.cognome,
        data_nascita=r.data_nascita,
        codice_fiscale=cf,
        email=r.email,
        telefono=r.telefono,
        cellulare=r.cellulare,
        sesso=r.sesso,
        sport=r.sport,
        comune_nascita=r.comune_nascita,
        provincia_nascita=r.provincia_nascita,
        stato_nascita=r.stato_nascita,
        indirizzo=r.indirizzo,
        comune_residenza=r.comune_residenza,
        provincia_residenza=r.provincia_residenza,
        cap_residenza=r.cap_residenza,
        genitore_id=genitore_id,
        e_socio=True,
    )
    db.add(tesserato)
    r.stato = "approvata"
    db.commit()
    return {"ok": True, "tesserato_id": tesserato.id}


@router.post("/iscrizioni/richieste/{richiesta_id}/rifiuta")
def rifiuta_richiesta(richiesta_id: int, db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    r = db.query(DatiRichiesta).filter(DatiRichiesta.id == richiesta_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Richiesta non trovata")
    r.stato = "rifiutata"
    db.commit()
    return {"ok": True}


# ---- PUBBLICO: compilazione modulo (senza auth) ----

@router.get("/iscriviti/{token}")
def get_modulo_pubblico(token: str, db: Session = Depends(get_db)):
    modulo = db.query(RichiestaIscrizione).filter(
        RichiestaIscrizione.token == token,
        RichiestaIscrizione.attivo == True
    ).first()
    if not modulo:
        raise HTTPException(status_code=404, detail="Modulo non trovato o non attivo")
    return {"id": modulo.id, "nome_modulo": modulo.nome_modulo}


@router.post("/iscriviti/{token}")
def invia_iscrizione(token: str, dati: DatiIscrizioneInput, db: Session = Depends(get_db)):
    modulo = db.query(RichiestaIscrizione).filter(
        RichiestaIscrizione.token == token,
        RichiestaIscrizione.attivo == True
    ).first()
    if not modulo:
        raise HTTPException(status_code=404, detail="Modulo non trovato o non attivo")
    if not dati.consenso_privacy:
        raise HTTPException(status_code=400, detail="È necessario accettare la privacy policy")

    richiesta = DatiRichiesta(
        modulo_id=modulo.id,
        stato="in_attesa",
        data_invio=datetime.now().strftime("%Y-%m-%d %H:%M"),
        **dati.model_dump()
    )
    db.add(richiesta)
    db.commit()
    return {"ok": True, "messaggio": "Iscrizione inviata con successo! La segreteria la contatterà presto."}
