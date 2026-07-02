from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.utenti import Tesserato, GruppoTesserato, Gruppo
from app.models.messaggi import Messaggio, MessaggioDestinatario
from app.schemas.messaggi import MessaggioCreate, MessaggioRead
import smtplib
import threading
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
        with smtplib.SMTP(host, porta, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(utente, password)
            server.sendmail(mittente, destinatario, msg.as_string())
        print(f"Email inviata a {destinatario}")
        return True
    except Exception as e:
        print(f"Errore invio email a {destinatario}: {e}")
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

    # Salva subito i destinatari senza aspettare le email
    lista_email = []
    for t in tesserati:
        email_dest = t.email if t.email else None
        if not email_dest and t.utente_id:
            from app.models.utenti import Utente
            utente = db.query(Utente).filter(Utente.id == t.utente_id).first()
            if utente and utente.email:
                email_dest = utente.email
        db.add(MessaggioDestinatario(
            messaggio_id=messaggio.id,
            tesserato_id=t.id,
            email_inviata=False,
        ))
        if email_dest:
            lista_email.append((t.id, email_dest))

    db.commit()

    # Invia email in background senza bloccare la risposta
    def invia_in_background(messaggio_id, emails, intestazione, corpo):
        from app.database import SessionLocal as SL
        bg_db = SL()
        try:
            for tesserato_id, email_dest in emails:
                ok = invia_email(email_dest, intestazione, corpo)
                if ok:
                    dest = bg_db.query(MessaggioDestinatario).filter(
                        MessaggioDestinatario.messaggio_id == messaggio_id,
                        MessaggioDestinatario.tesserato_id == tesserato_id
                    ).first()
                    if dest:
                        dest.email_inviata = True
                        bg_db.commit()
        finally:
            bg_db.close()

    thread = threading.Thread(
        target=invia_in_background,
        args=(messaggio.id, lista_email, dati.intestazione, dati.corpo),
        daemon=True
    )
    thread.start()
    db.refresh(messaggio)
    num_dest = db.query(MessaggioDestinatario).filter(MessaggioDestinatario.messaggio_id == messaggio.id).count()
    num_email = db.query(MessaggioDestinatario).filter(
        MessaggioDestinatario.messaggio_id == messaggio.id,
        MessaggioDestinatario.email_inviata == True
    ).count()
    return {
        "id": messaggio.id,
        "intestazione": messaggio.intestazione,
        "corpo": messaggio.corpo,
        "data_invio": messaggio.data_invio,
        "num_destinatari": num_dest,
        "num_email_inviate": num_email
    }


@router.get("/test-email")
def test_email(destinatario: str, db: Session = Depends(get_db)):
    import os
    host = os.getenv("EMAIL_HOST")
    porta = os.getenv("EMAIL_PORT")
    utente = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    ok = invia_email(destinatario, "Test Golè", "Email di test dal sistema Golè")
    return {
        "host": host,
        "porta": porta,
        "utente": utente,
        "password_presente": bool(password),
        "invio_ok": ok
    }


@router.get("/tesserato/{tesserato_id}", response_model=list[MessaggioRead])
def messaggi_tesserato(tesserato_id: int, db: Session = Depends(get_db)):
    destinatari = db.query(MessaggioDestinatario).filter(
        MessaggioDestinatario.tesserato_id == tesserato_id
    ).all()
    messaggi_ids = [d.messaggio_id for d in destinatari]
    messaggi = db.query(Messaggio).filter(
        Messaggio.id.in_(messaggi_ids)
    ).order_by(Messaggio.data_invio.desc()).all()
    result = []
    for m in messaggi:
        result.append({
            "id": m.id,
            "intestazione": m.intestazione,
            "corpo": m.corpo,
            "data_invio": m.data_invio,
            "num_destinatari": 1,
            "num_email_inviate": 0
        })
    return result


@router.get("/", response_model=list[MessaggioRead])
def lista_messaggi(db: Session = Depends(get_db)):
    messaggi = db.query(Messaggio).order_by(Messaggio.data_invio.desc()).all()
    result = []
    for m in messaggi:
        num_dest = db.query(MessaggioDestinatario).filter(MessaggioDestinatario.messaggio_id == m.id).count()
        num_email = db.query(MessaggioDestinatario).filter(
            MessaggioDestinatario.messaggio_id == m.id,
            MessaggioDestinatario.email_inviata == True
        ).count()
        result.append({
            "id": m.id,
            "intestazione": m.intestazione,
            "corpo": m.corpo,
            "data_invio": m.data_invio,
            "num_destinatari": num_dest,
            "num_email_inviate": num_email
        })
    return result
