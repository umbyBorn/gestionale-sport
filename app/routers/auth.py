from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.utenti import Utente, RuoloEnum
from app.auth import hash_password, verifica_password, crea_token, get_utente_corrente
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Autenticazione"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UtenteCreate(BaseModel):
    email: str
    password: str
    ruolo: RuoloEnum

class UtenteRead(BaseModel):
    id: int
    email: str
    ruolo: RuoloEnum
    attivo: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    ruolo: str
    tesserato_id: Optional[int] = None
    permessi: Optional[dict] = {}

@router.post("/registra", response_model=UtenteRead)
def registra_utente(utente: UtenteCreate, db: Session = Depends(get_db)):
    esistente = db.query(Utente).filter(Utente.email == utente.email).first()
    if esistente:
        raise HTTPException(status_code=400, detail="Email già registrata")
    db_utente = Utente(
        email=utente.email,
        password_hash=hash_password(utente.password),
        ruolo=utente.ruolo
    )
    db.add(db_utente)
    db.commit()
    db.refresh(db_utente)
    return db_utente

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    utente = db.query(Utente).filter(Utente.email == form_data.username).first()
    if not utente or not verifica_password(form_data.password, utente.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password errati",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not utente.attivo:
        raise HTTPException(status_code=403, detail="Account disabilitato")

    from app.models.utenti import Tesserato, PermessoOperatore
    tesserato = db.query(Tesserato).filter(Tesserato.utente_id == utente.id).first()
    permessi = db.query(PermessoOperatore).filter(PermessoOperatore.utente_id == utente.id).all()
    permessi_dict = {p.sezione: p.abilitato for p in permessi}

    token = crea_token({
        "sub": utente.email,
        "ruolo": utente.ruolo.value,
        "tesserato_id": tesserato.id if tesserato else None,
        "permessi": permessi_dict
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "ruolo": utente.ruolo.value,
        "tesserato_id": tesserato.id if tesserato else None,
        "permessi": permessi_dict
    }

@router.get("/me", response_model=UtenteRead)
def profilo(utente: Utente = Depends(get_utente_corrente)):
    return utente
