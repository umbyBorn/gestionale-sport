from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.staff import Staff, Compenso, Contratto, StaffGruppo
from app.models.utenti import Gruppo
from app.schemas.staff import (
    StaffCreate, StaffRead, CompensoCreate, CompensoRead,
    ContrattoCreate, ContrattoRead,
)
from typing import List
from pydantic import BaseModel

router = APIRouter(tags=["Staff"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- STAFF ----

@router.get("/staff/", response_model=List[StaffRead])
def lista_staff(db: Session = Depends(get_db)):
    return db.query(Staff).filter(Staff.attivo == True).all()

@router.get("/staff/tabulato/tessere")
def tabulato_tessere(db: Session = Depends(get_db)):
    """Elenco tessere emesse, per la stampa del tabulato soci."""
    soci = db.query(Staff).filter(Staff.numero_tessera.isnot(None)).order_by(Staff.numero_tessera.asc()).all()
    return [
        {
            "numero_tessera": s.numero_tessera,
            "cognome": s.cognome,
            "nome": s.nome,
            "data_nascita": s.data_nascita,
            "data_emissione_tessera": s.data_emissione_tessera,
            "quota_associativa": float(s.quota_associativa) if s.quota_associativa else None,
            "quota_pagata": s.quota_pagata,
            "attivo": s.attivo,
        }
        for s in soci
    ]

@router.get("/staff/{staff_id}", response_model=StaffRead)
def get_staff(staff_id: int, db: Session = Depends(get_db)):
    membro = db.query(Staff).filter(Staff.id == staff_id).first()
    if not membro:
        raise HTTPException(status_code=404, detail="Membro staff non trovato")
    return membro

@router.post("/staff/", response_model=StaffRead)
def crea_staff(membro: StaffCreate, db: Session = Depends(get_db)):
    dati = membro.model_dump()
    if not dati.get("numero_tessera"):
        massimo = db.query(Staff.numero_tessera).order_by(Staff.numero_tessera.desc()).first()
        dati["numero_tessera"] = (massimo[0] + 1) if massimo and massimo[0] else 1
    if not dati.get("data_emissione_tessera"):
        from datetime import date as _date
        dati["data_emissione_tessera"] = _date.today()
    db_membro = Staff(**dati)
    db.add(db_membro)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Numero tessera già assegnato a un altro socio")
    db.refresh(db_membro)
    return db_membro

@router.put("/staff/{staff_id}", response_model=StaffRead)
def aggiorna_staff(staff_id: int, membro: StaffCreate, db: Session = Depends(get_db)):
    db_membro = db.query(Staff).filter(Staff.id == staff_id).first()
    if not db_membro:
        raise HTTPException(status_code=404, detail="Membro staff non trovato")
    for key, value in membro.model_dump().items():
        setattr(db_membro, key, value)
    db.commit()
    db.refresh(db_membro)
    return db_membro

@router.delete("/staff/{staff_id}")
def elimina_staff(staff_id: int, db: Session = Depends(get_db)):
    db_membro = db.query(Staff).filter(Staff.id == staff_id).first()
    if not db_membro:
        raise HTTPException(status_code=404, detail="Membro staff non trovato")
    db_membro.attivo = False
    db.commit()
    return {"messaggio": "Membro staff disattivato"}


# ---- GRUPPI ASSEGNATI ALLO STAFF ----

class GruppiStaffUpdate(BaseModel):
    gruppo_ids: List[int]

@router.get("/staff/{staff_id}/gruppi")
def gruppi_staff(staff_id: int, db: Session = Depends(get_db)):
    righe = db.query(StaffGruppo).filter(StaffGruppo.staff_id == staff_id).all()
    gruppo_ids = [r.gruppo_id for r in righe]
    return db.query(Gruppo).filter(Gruppo.id.in_(gruppo_ids)).all() if gruppo_ids else []

@router.put("/staff/{staff_id}/gruppi")
def aggiorna_gruppi_staff(staff_id: int, dati: GruppiStaffUpdate, db: Session = Depends(get_db)):
    for riga in db.query(StaffGruppo).filter(StaffGruppo.staff_id == staff_id).all():
        db.delete(riga)
    for gid in dati.gruppo_ids:
        db.add(StaffGruppo(staff_id=staff_id, gruppo_id=gid))
    db.commit()
    return {"messaggio": "Gruppi aggiornati"}


# ---- COMPENSI ----

@router.get("/staff/{staff_id}/compensi", response_model=List[CompensoRead])
def lista_compensi(staff_id: int, db: Session = Depends(get_db)):
    return db.query(Compenso).filter(Compenso.staff_id == staff_id).order_by(Compenso.data_erogazione.desc()).all()

def _ricalcola_progressivi(db: Session, staff_id: int):
    """Ricalcola il totale progressivo e la soglia per tutti i compensi di un membro, in ordine cronologico."""
    compensi = db.query(Compenso).filter(Compenso.staff_id == staff_id).order_by(Compenso.data_erogazione).all()
    totale = 0.0
    for c in compensi:
        totale += float(c.importo)
        c.totale_progressivo = totale
        c.soglia_superata = totale >= 5000
    db.commit()

@router.post("/compensi/", response_model=CompensoRead)
def registra_compenso(compenso: CompensoCreate, db: Session = Depends(get_db)):
    db_compenso = Compenso(**compenso.model_dump(), totale_progressivo=0, soglia_superata=False)
    db.add(db_compenso)
    db.commit()
    _ricalcola_progressivi(db, compenso.staff_id)
    db.refresh(db_compenso)
    return db_compenso

@router.put("/compensi/{compenso_id}", response_model=CompensoRead)
def aggiorna_compenso(compenso_id: int, compenso: CompensoCreate, db: Session = Depends(get_db)):
    db_compenso = db.query(Compenso).filter(Compenso.id == compenso_id).first()
    if not db_compenso:
        raise HTTPException(status_code=404, detail="Compenso non trovato")
    for key, value in compenso.model_dump().items():
        setattr(db_compenso, key, value)
    db.commit()
    _ricalcola_progressivi(db, db_compenso.staff_id)
    db.refresh(db_compenso)
    return db_compenso

@router.delete("/compensi/{compenso_id}")
def elimina_compenso(compenso_id: int, db: Session = Depends(get_db)):
    db_compenso = db.query(Compenso).filter(Compenso.id == compenso_id).first()
    if not db_compenso:
        raise HTTPException(status_code=404, detail="Compenso non trovato")
    staff_id = db_compenso.staff_id
    db.delete(db_compenso)
    db.commit()
    _ricalcola_progressivi(db, staff_id)
    return {"messaggio": "Compenso eliminato"}


# ---- CONTRATTI ----

@router.get("/staff/{staff_id}/contratti", response_model=List[ContrattoRead])
def lista_contratti(staff_id: int, db: Session = Depends(get_db)):
    return db.query(Contratto).filter(Contratto.staff_id == staff_id).order_by(Contratto.data_inizio.desc()).all()

@router.post("/contratti/", response_model=ContrattoRead)
def crea_contratto(contratto: ContrattoCreate, db: Session = Depends(get_db)):
    db_contratto = Contratto(**contratto.model_dump())
    db.add(db_contratto)
    db.commit()
    db.refresh(db_contratto)
    return db_contratto

@router.put("/contratti/{contratto_id}", response_model=ContrattoRead)
def aggiorna_contratto(contratto_id: int, contratto: ContrattoCreate, db: Session = Depends(get_db)):
    db_contratto = db.query(Contratto).filter(Contratto.id == contratto_id).first()
    if not db_contratto:
        raise HTTPException(status_code=404, detail="Contratto non trovato")
    for key, value in contratto.model_dump().items():
        setattr(db_contratto, key, value)
    db.commit()
    db.refresh(db_contratto)
    return db_contratto

@router.delete("/contratti/{contratto_id}")
def elimina_contratto(contratto_id: int, db: Session = Depends(get_db)):
    db_contratto = db.query(Contratto).filter(Contratto.id == contratto_id).first()
    if not db_contratto:
        raise HTTPException(status_code=404, detail="Contratto non trovato")
    db.delete(db_contratto)
    db.commit()
    return {"messaggio": "Contratto eliminato"}


# ---- SOCI: modulo firmato e tabulato tessere ----

import os
import cloudinary
import cloudinary.uploader

cloudinary.config(cloudinary_url=os.getenv("CLOUDINARY_URL"))


@router.post("/staff/{staff_id}/modulo", response_model=StaffRead)
async def carica_modulo_firmato(staff_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_membro = db.query(Staff).filter(Staff.id == staff_id).first()
    if not db_membro:
        raise HTTPException(status_code=404, detail="Socio non trovato")
    contenuto = await file.read()
    nome_base, estensione = os.path.splitext(file.filename)
    public_id_finale = f"modulo_socio_{staff_id}_{nome_base.replace(' ', '_')}{estensione}"
    risultato = cloudinary.uploader.upload(
        contenuto,
        folder="gestionale/soci/moduli",
        resource_type="raw",
        public_id=public_id_finale,
        use_filename=False,
        unique_filename=True,
        overwrite=True,
        type="upload",
        access_mode="public",
    )
    db_membro.path_modulo_firmato = risultato["secure_url"]
    db.commit()
    db.refresh(db_membro)
    return db_membro


@router.get("/staff/{staff_id}/tessera/pdf")
def genera_tessera(staff_id: int, db: Session = Depends(get_db)):
    """Genera la tessera associativa PGS Juvenilia del socio, con logo."""
    from fastapi.responses import StreamingResponse
    from reportlab.lib.pagesizes import landscape
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    import io
    import requests as _requests

    socio = db.query(Staff).filter(Staff.id == staff_id).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio non trovato")
    if not socio.numero_tessera:
        raise HTTPException(status_code=400, detail="Nessun numero tessera assegnato a questo socio")

    LARGHEZZA, ALTEZZA = 9.5*cm, 6*cm
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(LARGHEZZA, ALTEZZA))

    c.setFillColor(HexColor("#1d4ed8"))
    c.rect(0, 0, LARGHEZZA, ALTEZZA, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.roundRect(0.25*cm, 0.25*cm, LARGHEZZA - 0.5*cm, ALTEZZA - 0.5*cm, 6, fill=1, stroke=0)

    try:
        logo_url = "https://res.cloudinary.com/srjdjqvl/image/upload/v1783538588/logo2_gijh4j.jpg"
        img_bytes = _requests.get(logo_url, timeout=10).content
        from reportlab.lib.utils import ImageReader
        logo = ImageReader(io.BytesIO(img_bytes))
        c.drawImage(logo, 0.5*cm, ALTEZZA - 2*cm, width=1.5*cm, height=1.5*cm, mask='auto')
    except Exception:
        pass

    c.setFillColor(HexColor("#1d4ed8"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2.2*cm, ALTEZZA - 1.1*cm, "ASD PGS JUVENILIA")
    c.setFont("Helvetica", 7)
    c.drawString(2.2*cm, ALTEZZA - 1.6*cm, "Tessera Socio")

    c.setFillColor(HexColor("#111827"))
    c.setFont("Helvetica-Bold", 13)
    c.drawString(0.6*cm, ALTEZZA - 2.6*cm, f"{socio.cognome} {socio.nome}")
    c.setFont("Helvetica", 9)
    if socio.data_nascita:
        c.drawString(0.6*cm, ALTEZZA - 3.2*cm, f"Nato/a il {socio.data_nascita.strftime('%d/%m/%Y')}")

    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.6*cm, 1*cm, f"N. TESSERA: {socio.numero_tessera}")
    c.setFont("Helvetica", 8)
    if socio.data_emissione_tessera:
        c.drawString(0.6*cm, 0.5*cm, f"Emessa il {socio.data_emissione_tessera.strftime('%d/%m/%Y')}")

    c.showPage()
    c.save()
    buffer.seek(0)
    nome_file = f"tessera_{socio.numero_tessera}_{socio.cognome}_{socio.nome}.pdf".replace(' ', '_')
    return StreamingResponse(
        buffer, media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nome_file}"'}
    )
def genera_modulo_adesione(staff_id: int, minorenne: bool = False, db: Session = Depends(get_db)):
    """Genera il modulo di richiesta adesione all'associazione, precompilato
    con i dati anagrafici del socio, pronto da stampare/far firmare."""
    from fastapi.responses import StreamingResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    import io

    socio = db.query(Staff).filter(Staff.id == staff_id).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio non trovato")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
    stili = getSampleStyleSheet()
    titolo = ParagraphStyle('titolo', parent=stili['Title'], fontSize=13, alignment=TA_CENTER)
    normale = ParagraphStyle('normale', parent=stili['Normal'], fontSize=11, spaceAfter=10, leading=16)

    elementi = [
        Paragraph('MODULO DI RICHIESTA ADESIONE ASSOCIAZIONE SPORTIVA<br/>"ASD P.G.S. JUVENILIA"', titolo),
        Spacer(1, 0.8*cm),
        Paragraph('Al Consiglio Direttivo dell\'Associazione Sportiva "ASD P.G.S. JUVENILIA", Codice Fiscale 93162560179', normale),
        Spacer(1, 0.5*cm),
        Paragraph(f'La/il sottoscritta/o <b>{socio.cognome} {socio.nome}</b>', normale),
        Paragraph(f'Nata/o a ____________________ il <b>{socio.data_nascita.strftime("%d/%m/%Y") if socio.data_nascita else "____________"}</b> Prov. ______', normale),
        Paragraph(f'Codice Fiscale <b>{socio.codice_fiscale or "________________________"}</b>', normale),
        Paragraph(f'Residente in <b>{socio.comune_residenza or "________________________"}</b> Prov. ______', normale),
        Paragraph(f'Indirizzo <b>{socio.indirizzo or "________________________"}</b> CAP ______', normale),
        Paragraph(f'Telefono <b>{socio.telefono or "____________"}</b> e-mail <b>{socio.email or "____________"}</b>', normale),
    ]

    if minorenne:
        elementi.append(Spacer(1, 0.3*cm))
        elementi.append(Paragraph(
            'In qualità di genitore/tutore di ______________________________ '
            'nato a _______________________ il ________________ '
            'C.F. _____________________________.', normale
        ))

    elementi += [
        Spacer(1, 0.5*cm),
        Paragraph('Avendo preso visione dello Statuto dell\'Associazione', normale),
        Paragraph('<b>Chiede</b>', normale),
        Paragraph(
            'Di poter aderire all\'associazione sportiva "ASD P.G.S. JUVENILIA" in qualità di Socio Ordinario. '
            f'A tal fine effettua il versamento della quota associativa annuale pari a '
            f'<b>{float(socio.quota_associativa):.2f} euro</b>.', normale
        ),
        Paragraph(
            'Dichiara di aver letto lo statuto e di attenersi ad eventuali regolamenti dell\'Associazione '
            'oltre che alle deliberazioni adottate dagli organi sociali.', normale
        ),
        Spacer(1, 1.5*cm),
        Paragraph('Luogo e data _____________________________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Firma _____________________________', normale),
    ]

    doc.build(elementi)
    buffer.seek(0)
    nome_file = f"modulo_adesione_{'minorenne' if minorenne else 'maggiorenne'}_{socio.cognome}_{socio.nome}.pdf".replace(' ', '_')
    return StreamingResponse(
        buffer, media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nome_file}"'}
    )

