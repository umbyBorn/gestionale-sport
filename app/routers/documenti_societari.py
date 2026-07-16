"""
Archivio dei documenti a livello di associazione (non legati a un singolo tesserato):
atto costitutivo, attribuzione codice fiscale, statuto, verbali di assemblea, ecc.
Riusa lo stesso meccanismo di upload su Cloudinary già in uso per i documenti dei tesserati.
"""
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.database import SessionLocal
from app.models.utenti import DocumentoSocietario
from app.auth import richiedi_ruolo
import cloudinary
import cloudinary.uploader
import os

cloudinary.config(cloudinary_url=os.getenv("CLOUDINARY_URL"))

router = APIRouter(prefix="/documenti-societari", tags=["Documenti societari"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DocumentoSocietarioRead(BaseModel):
    id: int
    nome: str
    categoria: Optional[str] = None
    nome_file: str
    url: str
    data_caricamento: date
    note: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[DocumentoSocietarioRead])
def lista_documenti_societari(db: Session = Depends(get_db)):
    return db.query(DocumentoSocietario).order_by(DocumentoSocietario.data_caricamento.desc()).all()


@router.post("/", response_model=DocumentoSocietarioRead)
async def carica_documento_societario(
    nome: str = Form(...),
    categoria: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin=Depends(richiedi_ruolo("amministratore")),
):
    contenuto = await file.read()
    nome_base, estensione = os.path.splitext(file.filename)
    nome_base_pulito = nome_base.replace(' ', '_')
    public_id_finale = f"{nome_base_pulito}{estensione}"  # mantiene l'estensione: fondamentale per raw
    risultato = cloudinary.uploader.upload(
        contenuto,
        folder="gestionale/documenti_societari",
        resource_type="raw",
        public_id=public_id_finale,
        use_filename=False,  # usiamo il public_id già pronto sopra
        unique_filename=True,
        overwrite=False,
        type="upload",
        access_mode="public",
    )
    doc = DocumentoSocietario(
        nome=nome,
        categoria=categoria,
        nome_file=file.filename,  # nome originale (con spazi) mostrato/usato in fase di download
        url=risultato["secure_url"],
        data_caricamento=datetime.now().date(),
        note=note,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{documento_id}")
def elimina_documento_societario(
    documento_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(richiedi_ruolo("amministratore")),
):
    doc = db.query(DocumentoSocietario).filter(DocumentoSocietario.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento non trovato")
    db.delete(doc)
    db.commit()
    return {"messaggio": "Documento eliminato"}
