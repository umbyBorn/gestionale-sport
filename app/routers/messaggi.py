from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.utenti import Tesserato, GruppoTesserato, Gruppo
from app.models.messaggi import Messaggio, MessaggioDestinatario
from app.schemas.messaggi import MessaggioCreate, MessaggioRead
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

router = APIRouter(prefix="/messaggi", tags=["Messaggi"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def invia_email(destinatario: str, intestazione: str, corpo: str):
    host = os.getenv("EMAIL_HOST")
    porta = int(os.getenv("EMAIL_PORT", "587"))
    utente = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    mittente = os.getenv("EMAIL_FROM", utente)

    if not host or not utente or not password:
        return False

    msg = MIMEMultipart()
    msg["From"] = mittente
    msg["To"] = destinatario
    msg["Subject"] = intestazione
    msg.attach(MIMEText(corpo, "plain"))

    try:
        with smtplib.SMTP(host, porta) as server:
            server.starttls()
            server.login(utente, password)
            server.sendmail(mittente, destinatario, msg.as_string())
        return True
    except Exception:
        return False


@router.get("/gruppi/{gruppo_id}/tesserati")
def tesserati_del_gruppo(gruppo_id: int, db: Session = Depends(get_db)):
    gruppo = db.query(Gruppo).filter(Gruppo.id == gruppo_id).first()
    if not gruppo:
        raise HTTPException(status_code=404, detail="Gruppo non trovato")

    tesserati = (
        db.query(Tesserato)
        .join(GruppoTesserato, GruppoTesserato.tesserato_id == Tesserato.id)
        .filter(GruppoTesserato.gruppo_id == gruppo_id, Tesserato.attivo == True)
        .all()
    )
    return [{"id": t.id, "nome": t.nome, "cognome": t.cognome} for t in tesserati]


@router.post("/invia", response_model=MessaggioRead)
def invia_messaggio(dati: MessaggioCreate, db: Session = Depends(get_db)):
    if not dati.intestazione.strip() or not dati.corpo.strip():
        raise HTTPException(status_code=400, detail="Intestazione e corpo del messaggio sono obbligatori")

    id_destinatari = set()

    if dati.gruppi_id:
        righe = (
            db.query(GruppoTesserato.tesserato_id)
            .filter(GruppoTesserato.gruppo_id.in_(dati.gruppi_id))
            .all()
        )
        id_destinatari.update(r[0] for r in righe)

    id_destinatari.update(dati.tesserati_aggiuntivi_id)
    id_destinatari -= set(dati.tesserati_esclusi_id)

    if not id_destinatari:
        raise HTTPException(status_code=400, detail="Nessun destinatario selezionato")

    messaggio = Messaggio(intestazione=dati.intestazione, corpo=dati.corpo)
    db.add(messaggio)
    db.flush()

    tesserati = db.query(Tesserato).filter(Tesserato.id.in_(id_destinatari)).all()

    for t in tesserati:
        email_ok = False
        if t.utente_id:
            from app.models.utenti import Utente
            utente = db.query(Utente).filter(Utente.id == t.utente_id).first()
            if utente and utente.email:
                email_ok = invia_email(utente.email, dati.intestazione, dati.corpo)

        db.add(MessaggioDestinatario(
            messaggio_id=messaggio.id,
            tesserato_id=t.id,
            email_inviata=email_ok,
        ))

    db.commit()
    db.refresh(messaggio)
    return messaggio


@router.get("/", response_model=list[MessaggioRead])
def lista_messaggi(db: Session = Depends(get_db)):
    return db.query(Messaggio).order_by(Messaggio.data_invio.desc()).all()
