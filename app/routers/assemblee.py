from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.assemblee import Assemblea, PuntoOrdineGiorno, PartecipazioneAssemblea
from app.schemas.assemblee import AssembleaCreate, AssembleaRead, PuntoOrdineGiornoCreate, PuntoOrdineGiornoRead, PartecipazioneCreate, PartecipazioneRead
from typing import List
import os
import cloudinary
import cloudinary.uploader

router = APIRouter(tags=["Assemblee"])

cloudinary.config(cloudinary_url=os.getenv("CLOUDINARY_URL"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- ASSEMBLEE ----

@router.get("/assemblee/", response_model=List[AssembleaRead])
def lista_assemblee(db: Session = Depends(get_db)):
    return db.query(Assemblea).all()

@router.get("/assemblee/{assemblea_id}", response_model=AssembleaRead)
def get_assemblea(assemblea_id: int, db: Session = Depends(get_db)):
    assemblea = db.query(Assemblea).filter(Assemblea.id == assemblea_id).first()
    if not assemblea:
        raise HTTPException(status_code=404, detail="Assemblea non trovata")
    return assemblea

@router.post("/assemblee/", response_model=AssembleaRead)
def crea_assemblea(assemblea: AssembleaCreate, db: Session = Depends(get_db)):
    db_assemblea = Assemblea(**assemblea.model_dump())
    db.add(db_assemblea)
    db.commit()
    db.refresh(db_assemblea)
    return db_assemblea

@router.put("/assemblee/{assemblea_id}", response_model=AssembleaRead)
def aggiorna_assemblea(assemblea_id: int, assemblea: AssembleaCreate, db: Session = Depends(get_db)):
    db_assemblea = db.query(Assemblea).filter(Assemblea.id == assemblea_id).first()
    if not db_assemblea:
        raise HTTPException(status_code=404, detail="Assemblea non trovata")
    for key, value in assemblea.model_dump().items():
        setattr(db_assemblea, key, value)
    db.commit()
    db.refresh(db_assemblea)
    return db_assemblea

@router.delete("/assemblee/{assemblea_id}")
def elimina_assemblea(assemblea_id: int, db: Session = Depends(get_db)):
    db_assemblea = db.query(Assemblea).filter(Assemblea.id == assemblea_id).first()
    if not db_assemblea:
        raise HTTPException(status_code=404, detail="Assemblea non trovata")
    db.delete(db_assemblea)
    db.commit()
    return {"messaggio": "Assemblea eliminata"}

# ---- PUNTI ORDINE DEL GIORNO ----

@router.get("/assemblee/{assemblea_id}/punti", response_model=List[PuntoOrdineGiornoRead])
def lista_punti(assemblea_id: int, db: Session = Depends(get_db)):
    return db.query(PuntoOrdineGiorno).filter(PuntoOrdineGiorno.assemblea_id == assemblea_id).all()

@router.post("/punti/", response_model=PuntoOrdineGiornoRead)
def crea_punto(punto: PuntoOrdineGiornoCreate, db: Session = Depends(get_db)):
    db_punto = PuntoOrdineGiorno(**punto.model_dump())
    db.add(db_punto)
    db.commit()
    db.refresh(db_punto)
    return db_punto

@router.put("/punti/{punto_id}/esito", response_model=PuntoOrdineGiornoRead)
def aggiorna_esito(punto_id: int, esito: str, db: Session = Depends(get_db)):
    db_punto = db.query(PuntoOrdineGiorno).filter(PuntoOrdineGiorno.id == punto_id).first()
    if not db_punto:
        raise HTTPException(status_code=404, detail="Punto non trovato")
    db_punto.esito = esito
    db.commit()
    db.refresh(db_punto)
    return db_punto

# ---- PARTECIPAZIONI ----

@router.get("/assemblee/{assemblea_id}/partecipanti", response_model=List[PartecipazioneRead])
def lista_partecipanti(assemblea_id: int, db: Session = Depends(get_db)):
    return db.query(PartecipazioneAssemblea).filter(PartecipazioneAssemblea.assemblea_id == assemblea_id).all()

@router.post("/partecipazioni/", response_model=PartecipazioneRead)
def registra_partecipazione(partecipazione: PartecipazioneCreate, db: Session = Depends(get_db)):
    db_part = PartecipazioneAssemblea(**partecipazione.model_dump())
    db.add(db_part)
    db.commit()
    db.refresh(db_part)
    return db_part

@router.put("/partecipazioni/{partecipazione_id}", response_model=PartecipazioneRead)
def aggiorna_partecipazione(partecipazione_id: int, partecipazione: PartecipazioneCreate, db: Session = Depends(get_db)):
    db_part = db.query(PartecipazioneAssemblea).filter(PartecipazioneAssemblea.id == partecipazione_id).first()
    if not db_part:
        raise HTTPException(status_code=404, detail="Partecipazione non trovata")
    for key, value in partecipazione.model_dump().items():
        setattr(db_part, key, value)
    db.commit()
    db.refresh(db_part)
    return db_part


# ---- VERBALE ----

@router.post("/assemblee/{assemblea_id}/verbale", response_model=AssembleaRead)
async def carica_verbale(assemblea_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_assemblea = db.query(Assemblea).filter(Assemblea.id == assemblea_id).first()
    if not db_assemblea:
        raise HTTPException(status_code=404, detail="Assemblea non trovata")

    contenuto = await file.read()
    nome_base, estensione = os.path.splitext(file.filename)
    nome_base_pulito = nome_base.replace(' ', '_')
    public_id_finale = f"verbale_{assemblea_id}_{nome_base_pulito}{estensione}"
    risultato = cloudinary.uploader.upload(
        contenuto,
        folder="gestionale/assemblee/verbali",
        resource_type="raw",
        public_id=public_id_finale,
        use_filename=False,
        unique_filename=True,
        overwrite=True,
        type="upload",
        access_mode="public",
    )
    db_assemblea.path_verbale = risultato["secure_url"]
    db.commit()
    db.refresh(db_assemblea)
    return db_assemblea


@router.delete("/assemblee/{assemblea_id}/verbale", response_model=AssembleaRead)
def elimina_verbale(assemblea_id: int, db: Session = Depends(get_db)):
    db_assemblea = db.query(Assemblea).filter(Assemblea.id == assemblea_id).first()
    if not db_assemblea:
        raise HTTPException(status_code=404, detail="Assemblea non trovata")
    db_assemblea.path_verbale = None
    db.commit()
    db.refresh(db_assemblea)
    return db_assemblea
