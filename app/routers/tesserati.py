from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session, joinedload
from datetime import date
from app.database import SessionLocal
from app.models.utenti import Tesserato
from app.schemas.tesserati import TesseratoCreate, TesseratoRead
from typing import List, Optional

router = APIRouter(prefix="/tesserati", tags=["Tesserati"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/tutti", response_model=List[TesseratoRead])
def lista_tutti_tesserati(db: Session = Depends(get_db)):
    return db.query(Tesserato).options(joinedload(Tesserato.genitore), joinedload(Tesserato.documenti)).all()

@router.get("/", response_model=List[TesseratoRead])
def lista_tesserati(db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload as jl
    tesserati = db.query(Tesserato).options(
        jl(Tesserato.genitore),
        jl(Tesserato.documenti),
        jl(Tesserato.gruppi).joinedload(Tesserato.gruppi.property.mapper.class_.gruppo)
    ).filter(Tesserato.attivo == True).all()
    for t in tesserati:
        t.gruppi_nomi = [gt.gruppo.nome for gt in t.gruppi if gt.gruppo]
    return tesserati

@router.get("/{tesserato_id}", response_model=TesseratoRead)
def get_tesserato(tesserato_id: int, db: Session = Depends(get_db)):
    tesserato = db.query(Tesserato).options(joinedload(Tesserato.genitore), joinedload(Tesserato.documenti)).filter(Tesserato.id == tesserato_id).first()
    if not tesserato:
        raise HTTPException(status_code=404, detail="Tesserato non trovato")
    return tesserato

@router.post("/", response_model=TesseratoRead)
def crea_tesserato(tesserato: TesseratoCreate, db: Session = Depends(get_db)):
    db_tesserato = Tesserato(**tesserato.model_dump())
    db.add(db_tesserato)
    db.commit()
    db.refresh(db_tesserato)
    return db_tesserato

@router.put("/{tesserato_id}", response_model=TesseratoRead)
def aggiorna_tesserato(tesserato_id: int, tesserato: TesseratoCreate, db: Session = Depends(get_db)):
    db_tesserato = db.query(Tesserato).filter(Tesserato.id == tesserato_id).first()
    if not db_tesserato:
        raise HTTPException(status_code=404, detail="Tesserato non trovato")
    for key, value in tesserato.model_dump().items():
        setattr(db_tesserato, key, value)
    db.commit()
    db.refresh(db_tesserato)
    return db_tesserato

@router.put("/{tesserato_id}/riattiva", response_model=TesseratoRead)
def riattiva_tesserato(tesserato_id: int, db: Session = Depends(get_db)):
    db_tesserato = db.query(Tesserato).filter(Tesserato.id == tesserato_id).first()
    if not db_tesserato:
        raise HTTPException(status_code=404, detail="Tesserato non trovato")
    db_tesserato.attivo = True
    db.commit()
    db.refresh(db_tesserato)
    return db_tesserato

@router.delete("/{tesserato_id}")
def elimina_tesserato(tesserato_id: int, db: Session = Depends(get_db)):
    db_tesserato = db.query(Tesserato).filter(Tesserato.id == tesserato_id).first()
    if not db_tesserato:
        raise HTTPException(status_code=404, detail="Tesserato non trovato")
    db_tesserato.attivo = False
    db.commit()
    return {"messaggio": "Tesserato disattivato"}

@router.delete("/{tesserato_id}/definitivo")
def elimina_tesserato_definitivo(tesserato_id: int, db: Session = Depends(get_db)):
    db_tesserato = db.query(Tesserato).filter(Tesserato.id == tesserato_id).first()
    if not db_tesserato:
        raise HTTPException(status_code=404, detail="Tesserato non trovato")
    from app.models.utenti import Documento, GruppoTesserato
    db.query(Documento).filter(Documento.tesserato_id == tesserato_id).delete()
    db.query(GruppoTesserato).filter(GruppoTesserato.tesserato_id == tesserato_id).delete()
    db.delete(db_tesserato)
    db.commit()
    return {"messaggio": "Tesserato eliminato definitivamente"}
from app.models.utenti import GruppoTesserato, Gruppo
from datetime import date


@router.get("/{tesserato_id}/gruppi")
def gruppi_del_tesserato(tesserato_id: int, db: Session = Depends(get_db)):
    righe = db.query(GruppoTesserato).filter(GruppoTesserato.tesserato_id == tesserato_id).all()
    return [r.gruppo_id for r in righe]


@router.put("/{tesserato_id}/gruppi")
def aggiorna_gruppi_tesserato(tesserato_id: int, gruppi_id: list[int], db: Session = Depends(get_db)):
    db.query(GruppoTesserato).filter(GruppoTesserato.tesserato_id == tesserato_id).delete()
    for gid in gruppi_id:
        db.add(GruppoTesserato(gruppo_id=gid, tesserato_id=tesserato_id, data_iscrizione=date.today()))
    db.commit()
    return {"ok": True, "gruppi_assegnati": gruppi_id}

# ---- GENITORI ----
from app.schemas.tesserati import GenitoreCreate, GenitoreRead, DocumentoCreate, DocumentoRead
from app.models.utenti import Genitore, Documento
import cloudinary
import cloudinary.uploader
import os

cloudinary.config(cloudinary_url=os.getenv("CLOUDINARY_URL"))

@router.get("/genitori/", response_model=list[GenitoreRead])
def lista_genitori(db: Session = Depends(get_db)):
    return db.query(Genitore).all()

@router.post("/genitori/", response_model=GenitoreRead)
def crea_genitore(genitore: GenitoreCreate, db: Session = Depends(get_db)):
    g = Genitore(**genitore.model_dump())
    db.add(g)
    db.commit()
    db.refresh(g)
    return g

@router.put("/genitori/{genitore_id}", response_model=GenitoreRead)
def aggiorna_genitore(genitore_id: int, genitore: GenitoreCreate, db: Session = Depends(get_db)):
    g = db.query(Genitore).filter(Genitore.id == genitore_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Genitore non trovato")
    for key, value in genitore.model_dump().items():
        setattr(g, key, value)
    db.commit()
    db.refresh(g)
    return g

@router.delete("/genitori/{genitore_id}")
def elimina_genitore(genitore_id: int, db: Session = Depends(get_db)):
    g = db.query(Genitore).filter(Genitore.id == genitore_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Genitore non trovato")
    db.delete(g)
    db.commit()
    return {"messaggio": "Genitore eliminato"}


# ---- DOCUMENTI E FOTO ----
from fastapi import UploadFile, File

@router.get("/{tesserato_id}/documenti", response_model=list[DocumentoRead])
def lista_documenti(tesserato_id: int, db: Session = Depends(get_db)):
    return db.query(Documento).filter(Documento.tesserato_id == tesserato_id).all()

@router.post("/{tesserato_id}/documenti")
async def carica_documento(
    tesserato_id: int,
    tipo: str = Form(...),
    data_scadenza: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    contenuto = await file.read()
    risultato = cloudinary.uploader.upload(
        contenuto,
        folder=f"gestionale/tesserati/{tesserato_id}/documenti",
        resource_type="auto",
        public_id=file.filename
    )
    from datetime import datetime
    data_scad_parsed = None
    if data_scadenza:
        try:
            data_scad_parsed = datetime.strptime(data_scadenza, "%Y-%m-%d").date()
        except ValueError:
            pass
    doc = Documento(
        tesserato_id=tesserato_id,
        tipo=tipo,
        nome_file=file.filename,
        url=risultato["secure_url"],
        data_scadenza=data_scad_parsed,
        note=note
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.delete("/documenti/{documento_id}")
def elimina_documento(documento_id: int, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento non trovato")
    db.delete(doc)
    db.commit()
    return {"messaggio": "Documento eliminato"}

@router.post("/{tesserato_id}/foto")
async def carica_foto(
    tesserato_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    tesserato = db.query(Tesserato).filter(Tesserato.id == tesserato_id).first()
    if not tesserato:
        raise HTTPException(status_code=404, detail="Tesserato non trovato")
    contenuto = await file.read()
    risultato = cloudinary.uploader.upload(
        contenuto,
        folder=f"gestionale/tesserati/{tesserato_id}",
        resource_type="image",
        public_id="foto",
        overwrite=True,
        transformation=[{"width": 400, "height": 400, "crop": "fill", "gravity": "face"}]
    )
    tesserato.foto_url = risultato["secure_url"]
    db.commit()
    db.refresh(tesserato)
    return {"foto_url": tesserato.foto_url}
