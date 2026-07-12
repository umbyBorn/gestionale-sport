from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.utenti import Utente, RuoloEnum, PermessoOperatore, Tesserato
from app.auth import hash_password, get_utente_corrente
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/admin", tags=["Admin"])

SEZIONI_DISPONIBILI = [
    "tesserati", "gruppi", "pagamenti", "staff",
    "presenze", "assemblee", "calendario", "messaggi", "importazione"
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def solo_admin(utente: Utente = Depends(get_utente_corrente)):
    if utente.ruolo != RuoloEnum.amministratore:
        raise HTTPException(status_code=403, detail="Accesso riservato agli amministratori")
    return utente


class CreaUtenteInput(BaseModel):
    email: str
    password: str
    ruolo: RuoloEnum
    tesserato_id: Optional[int] = None


class PermessoInput(BaseModel):
    sezione: str
    abilitato: bool


@router.get("/utenti")
def lista_utenti(db: Session = Depends(get_db), _=Depends(solo_admin)):
    utenti = db.query(Utente).all()
    result = []
    for u in utenti:
        permessi = db.query(PermessoOperatore).filter(PermessoOperatore.utente_id == u.id).all()
        tesserato = db.query(Tesserato).filter(Tesserato.utente_id == u.id).first()
        result.append({
            "id": u.id,
            "email": u.email,
            "ruolo": u.ruolo.value,
            "attivo": u.attivo,
            "tesserato_id": tesserato.id if tesserato else None,
            "tesserato_nome": f"{tesserato.nome} {tesserato.cognome}" if tesserato else None,
            "permessi": {p.sezione: p.abilitato for p in permessi}
        })
    return result


@router.post("/utenti")
def crea_utente(dati: CreaUtenteInput, db: Session = Depends(get_db), _=Depends(solo_admin)):
    esistente = db.query(Utente).filter(Utente.email == dati.email).first()
    if esistente:
        raise HTTPException(status_code=400, detail="Email già registrata")
    utente = Utente(
        email=dati.email,
        password_hash=hash_password(dati.password),
        ruolo=dati.ruolo
    )
    db.add(utente)
    db.flush()
    if dati.tesserato_id:
        tesserato = db.query(Tesserato).filter(Tesserato.id == dati.tesserato_id).first()
        if tesserato:
            tesserato.utente_id = utente.id
    if dati.ruolo == RuoloEnum.operatore:
        for sezione in SEZIONI_DISPONIBILI:
            db.add(PermessoOperatore(utente_id=utente.id, sezione=sezione, abilitato=True))
    db.commit()
    db.refresh(utente)
    return {"id": utente.id, "email": utente.email, "ruolo": utente.ruolo.value}


@router.put("/utenti/{utente_id}/permesso")
def aggiorna_permesso(
    utente_id: int,
    dati: PermessoInput,
    db: Session = Depends(get_db),
    _=Depends(solo_admin)
):
    if dati.sezione not in SEZIONI_DISPONIBILI:
        raise HTTPException(status_code=400, detail=f"Sezione non valida: {dati.sezione}")
    permesso = db.query(PermessoOperatore).filter(
        PermessoOperatore.utente_id == utente_id,
        PermessoOperatore.sezione == dati.sezione
    ).first()
    if permesso:
        permesso.abilitato = dati.abilitato
    else:
        db.add(PermessoOperatore(utente_id=utente_id, sezione=dati.sezione, abilitato=dati.abilitato))
    db.commit()
    return {"ok": True}


class ModificaUtenteInput(BaseModel):
    email: Optional[str] = None
    ruolo: Optional[RuoloEnum] = None
    tesserato_id: Optional[int] = None


@router.put("/utenti/{utente_id}")
def modifica_utente(
    utente_id: int,
    dati: ModificaUtenteInput,
    db: Session = Depends(get_db),
    _=Depends(solo_admin),
):
    utente = db.query(Utente).filter(Utente.id == utente_id).first()
    if not utente:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    if dati.email and dati.email != utente.email:
        esistente = db.query(Utente).filter(Utente.email == dati.email, Utente.id != utente_id).first()
        if esistente:
            raise HTTPException(status_code=400, detail="Email già registrata da un altro utente")
        utente.email = dati.email
    if dati.ruolo:
        utente.ruolo = dati.ruolo
    if dati.tesserato_id is not None:
        # scollega il tesserato precedentemente associato a questo utente
        vecchio = db.query(Tesserato).filter(Tesserato.utente_id == utente_id).first()
        if vecchio:
            vecchio.utente_id = None
        if dati.tesserato_id:
            nuovo = db.query(Tesserato).filter(Tesserato.id == dati.tesserato_id).first()
            if nuovo:
                nuovo.utente_id = utente_id
    db.commit()
    db.refresh(utente)
    return {"id": utente.id, "email": utente.email, "ruolo": utente.ruolo.value}


@router.delete("/utenti/{utente_id}")
def elimina_utente(
    utente_id: int,
    db: Session = Depends(get_db),
    richiedente: Utente = Depends(solo_admin),
):
    if utente_id == richiedente.id:
        raise HTTPException(status_code=400, detail="Non puoi eliminare il tuo stesso account mentre sei collegato")
    utente = db.query(Utente).filter(Utente.id == utente_id).first()
    if not utente:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    # scollega eventuale tesserato associato (non lo elimina, solo rimuove il collegamento)
    tesserato = db.query(Tesserato).filter(Tesserato.utente_id == utente_id).first()
    if tesserato:
        tesserato.utente_id = None
    db.query(PermessoOperatore).filter(PermessoOperatore.utente_id == utente_id).delete()
    db.delete(utente)
    db.commit()
    return {"messaggio": "Utente eliminato definitivamente"}


@router.put("/utenti/{utente_id}/attivo")
def toggle_utente(utente_id: int, attivo: bool, db: Session = Depends(get_db), _=Depends(solo_admin)):
    utente = db.query(Utente).filter(Utente.id == utente_id).first()
    if not utente:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    utente.attivo = attivo
    db.commit()
    return {"ok": True}


@router.put("/utenti/{utente_id}/password")
def cambia_password(utente_id: int, nuova_password: str, db: Session = Depends(get_db), _=Depends(solo_admin)):
    utente = db.query(Utente).filter(Utente.id == utente_id).first()
    if not utente:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    utente.password_hash = hash_password(nuova_password)
    db.commit()
    return {"ok": True}


@router.get("/sezioni")
def lista_sezioni(_=Depends(solo_admin)):
    return SEZIONI_DISPONIBILI


@router.get("/permessi/{utente_id}")
def permessi_utente(utente_id: int, db: Session = Depends(get_db), _=Depends(solo_admin)):
    permessi = db.query(PermessoOperatore).filter(PermessoOperatore.utente_id == utente_id).all()
    return {p.sezione: p.abilitato for p in permessi}
