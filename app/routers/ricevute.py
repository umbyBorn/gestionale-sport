from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.utenti import Tesserato
from app.models.contabilita import Pagamento, Tariffa, RicevutaDonazione
from app.schemas.pagamenti import RicevutaDonazioneCreate, RicevutaDonazioneRead
from app.auth import get_utente_corrente
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
import requests
from datetime import datetime
from num2words import num2words

router = APIRouter(prefix="/ricevute", tags=["Ricevute"])

NOME_ASSOCIAZIONE = "ASD PGS Juvenilia"
CITTA_ASSOCIAZIONE = "Catania"
PRESIDENTE = "Sardo Carmela Linda"
LOGO_URL = "https://res.cloudinary.com/srjdjqvl/image/upload/v1783538588/logo2_gijh4j.jpg"
COLORE_PRIMARIO = HexColor("#1e3a8a")
COLORE_SECONDARIO = HexColor("#dc2626")

MESI_IT = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
]


def formatta_data_it(data_iso: str) -> str:
    """Converte una data ISO (aaaa-mm-gg) in formato italiano gg/mm/aaaa per la visualizzazione."""
    try:
        return datetime.strptime(str(data_iso)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return str(data_iso)


def importo_in_lettere(importo: float) -> str:
    """Converte un importo in euro nella dicitura in lettere usata sulle ricevute
    cartacee, es. 40.00 -> 'QUARANTA/00', 42.50 -> 'QUARANTADUE/50'."""
    euro = int(importo)
    centesimi = round((importo - euro) * 100)
    testo = num2words(euro, lang='it').upper()
    return f"{testo}/{centesimi:02d}"


def estrai_mese_competenza(causale: str, data_scadenza: str = None) -> str:
    """Cerca di individuare il mese di competenza della quota, prima dal nome
    della voce di pagamento (es. tariffa 'Settembre'), poi dalla data di scadenza."""
    causale_lower = (causale or "").lower()
    for mese in MESI_IT:
        if mese.lower() in causale_lower:
            return mese
    if data_scadenza:
        try:
            data_obj = datetime.strptime(str(data_scadenza)[:10], "%Y-%m-%d")
            return MESI_IT[data_obj.month - 1]
        except ValueError:
            pass
    return ""

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def scarica_logo():
    try:
        res = requests.get(LOGO_URL, timeout=5)
        return io.BytesIO(res.content)
    except:
        return None


def genera_pdf_ricevuta(
    numero: int,
    tesserato: Tesserato,
    importo: float,
    causale: str,
    data_pagamento: str,
    metodo: str,
    intestatario_nome: str = None,
    intestatario_doc: str = None,
    mese_competenza: str = None,
) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    elementi = []

    # Stile titolo
    stile_titolo = ParagraphStyle('titolo', fontSize=20, textColor=COLORE_PRIMARIO,
                                   spaceAfter=6, fontName='Helvetica-Bold', alignment=TA_CENTER)
    stile_sottotitolo = ParagraphStyle('sottotitolo', fontSize=11, textColor=COLORE_SECONDARIO,
                                        spaceAfter=4, fontName='Helvetica-Bold', alignment=TA_CENTER)
    stile_normale = ParagraphStyle('normale', fontSize=10, spaceAfter=4, fontName='Helvetica')
    stile_piccolo = ParagraphStyle('piccolo', fontSize=8, textColor=HexColor("#6b7280"), fontName='Helvetica')
    stile_destra = ParagraphStyle('destra', fontSize=10, alignment=TA_RIGHT, fontName='Helvetica')

    # HEADER — Logo + Nome associazione
    logo_data = scarica_logo()
    if logo_data:
        logo = Image(logo_data, width=3*cm, height=3*cm)
        logo.hAlign = 'LEFT'
        header_data = [[logo, Paragraph(f"<b>{NOME_ASSOCIAZIONE}</b><br/>{CITTA_ASSOCIAZIONE}", stile_titolo)]]
        header_table = Table(header_data, colWidths=[4*cm, 13*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
        ]))
        elementi.append(header_table)
    else:
        elementi.append(Paragraph(f"<b>{NOME_ASSOCIAZIONE}</b>", stile_titolo))
        elementi.append(Paragraph(CITTA_ASSOCIAZIONE, stile_sottotitolo))

    # Linea separatrice
    elementi.append(Spacer(1, 0.3*cm))
    linea = Table([['']], colWidths=[17*cm], rowHeights=[0.05*cm])
    linea.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), COLORE_PRIMARIO)]))
    elementi.append(linea)
    elementi.append(Spacer(1, 0.5*cm))

    # TITOLO RICEVUTA
    elementi.append(Paragraph(f"RICEVUTA DI PAGAMENTO N. {numero:04d}", stile_titolo))
    elementi.append(Spacer(1, 0.5*cm))
    elementi.append(Paragraph(
        f"Data: {formatta_data_it(data_pagamento)}",
        ParagraphStyle('data', fontSize=10, alignment=TA_CENTER, textColor=HexColor("#6b7280"), fontName='Helvetica')
    ))
    elementi.append(Spacer(1, 0.8*cm))

    # BOX DATI TESSERATO — se il tesserato ha un genitore associato, la ricevuta va intestata a lui
    nome_completo = intestatario_nome or f"{tesserato.nome} {tesserato.cognome}"
    cf = intestatario_doc or (tesserato.codice_fiscale if not tesserato.codice_fiscale.startswith('TEMP_') else '—')
    indirizzo = tesserato.indirizzo or '—'
    comune = f"{tesserato.comune_residenza or ''} {tesserato.provincia_residenza or ''}".strip() or '—'
    nome_atleta = f"{tesserato.nome} {tesserato.cognome}"

    elementi.append(Spacer(1, 0.3*cm))  # spazio extra dopo città
    dati_box = [
        [Paragraph('<b>INTESTATARIO</b>', ParagraphStyle('label', fontSize=8, textColor=white, fontName='Helvetica-Bold')), ''],
        [Paragraph(f'<b>{nome_completo}</b>', ParagraphStyle('nome', fontSize=13, textColor=COLORE_PRIMARIO, fontName='Helvetica-Bold')), ''],
        [Paragraph(f'Codice Fiscale: {cf}', stile_normale), Paragraph(f'Indirizzo: {indirizzo}', stile_normale)],
        [Paragraph(f'Comune: {comune}', stile_normale), ''],
    ]
    if intestatario_nome and intestatario_nome != nome_atleta:
        dati_box.append([Paragraph(f'Per conto di (atleta): <b>{nome_atleta}</b>', stile_normale), ''])

    box = Table(dati_box, colWidths=[8.5*cm, 8.5*cm])
    box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLORE_PRIMARIO),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('SPAN', (0,0), (-1,0)),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor("#eff6ff"), white]),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor("#e5e7eb")),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    elementi.append(box)
    elementi.append(Spacer(1, 0.8*cm))

    # DICHIARAZIONE FORMALE (dicitura ufficiale della ricevuta cartacea dell'associazione)
    lettere = importo_in_lettere(importo)
    riferimento_mese = f" a titolo di quota partecipazione attività per il mese di {mese_competenza}" if mese_competenza else " a titolo di quota partecipazione attività"
    stile_dichiarazione = ParagraphStyle(
        'dichiarazione', fontSize=10.5, fontName='Helvetica', leading=15,
        alignment=TA_LEFT, spaceAfter=4, borderPadding=8,
    )
    elementi.append(Paragraph(
        f"Si dichiara di ricevere da <b>{nome_completo}</b>, "
        f"€ {importo:.2f} (<b>{lettere}</b>){riferimento_mese}.",
        stile_dichiarazione
    ))
    elementi.append(Spacer(1, 0.6*cm))

    # DETTAGLIO PAGAMENTO
    dettaglio_header = [
        [Paragraph('<b>DESCRIZIONE</b>', ParagraphStyle('th', fontSize=9, textColor=white, fontName='Helvetica-Bold')),
         Paragraph('<b>METODO</b>', ParagraphStyle('th', fontSize=9, textColor=white, fontName='Helvetica-Bold', alignment=TA_CENTER)),
         Paragraph('<b>IMPORTO</b>', ParagraphStyle('th', fontSize=9, textColor=white, fontName='Helvetica-Bold', alignment=TA_RIGHT))],
        [Paragraph(causale, stile_normale),
         Paragraph(metodo.capitalize(), ParagraphStyle('metodo', fontSize=10, alignment=TA_CENTER, fontName='Helvetica')),
         Paragraph(f'€ {importo:.2f}', ParagraphStyle('importo', fontSize=10, alignment=TA_RIGHT, fontName='Helvetica-Bold', textColor=COLORE_PRIMARIO))],
        ['', '',
         Paragraph(f'<b>TOTALE: € {importo:.2f}</b>',
                   ParagraphStyle('totale', fontSize=12, alignment=TA_RIGHT, fontName='Helvetica-Bold', textColor=COLORE_SECONDARIO))],
    ]

    tabella = Table(dettaglio_header, colWidths=[9*cm, 4*cm, 4*cm])
    tabella.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLORE_PRIMARIO),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('BACKGROUND', (0,1), (-1,1), HexColor("#eff6ff")),
        ('BACKGROUND', (0,2), (-1,2), HexColor("#fef2f2")),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor("#e5e7eb")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('SPAN', (0,2), (1,2)),
    ]))
    elementi.append(tabella)
    elementi.append(Spacer(1, 1.5*cm))

    # FIRMA
    firma_data = [
        [Paragraph('Il Presidente', ParagraphStyle('firma_label', fontSize=9, textColor=HexColor("#6b7280"), fontName='Helvetica', alignment=TA_RIGHT)), ''],
        [Paragraph(f'<b>{PRESIDENTE}</b>', ParagraphStyle('firma_nome', fontSize=11, fontName='Helvetica-Bold', alignment=TA_RIGHT)), ''],
        [Paragraph('_________________________', ParagraphStyle('firma_linea', fontSize=11, alignment=TA_RIGHT, textColor=HexColor("#9ca3af"))), ''],
    ]
    firma_table = Table(firma_data, colWidths=[8.5*cm, 8.5*cm])
    firma_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elementi.append(firma_table)
    elementi.append(Spacer(1, 1*cm))

    # NOTE LEGALI
    linea2 = Table([['']], colWidths=[17*cm], rowHeights=[0.05*cm])
    linea2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), HexColor("#e5e7eb"))]))
    elementi.append(linea2)
    elementi.append(Spacer(1, 0.3*cm))
    elementi.append(Paragraph(
        "<u>Operazione non soggetta ad IVA ai sensi dell'art.4 quarto comma D.P.R. 633/1972</u>",
        ParagraphStyle('nota_iva', fontSize=9, fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=8)
    ))
    elementi.append(Paragraph(
        f"Ricevuta generata il {datetime.now().strftime('%d/%m/%Y alle %H:%M')} dal sistema gestionale PGS Juvenilia · {NOME_ASSOCIAZIONE} · {CITTA_ASSOCIAZIONE}",
        stile_piccolo
    ))

    doc.build(elementi)
    buffer.seek(0)
    return buffer


def genera_pdf_ricevuta_donazione(
    numero: int,
    nome_donatore: str,
    importo: float,
    data: str,
    causale: str = None,
) -> io.BytesIO:
    """Ricevuta per erogazione liberale (donazione) a sostegno dell'associazione.
    Dicitura legale distinta dalla ricevuta di quota: esenzione IVA ex art.2 c.3 lett.a)
    D.P.R. 633/72 e beneficio fiscale ex art.83 D.Lgs 117/2017 (Codice del Terzo Settore)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elementi = []

    stile_titolo = ParagraphStyle('titolo', fontSize=20, textColor=COLORE_PRIMARIO, spaceAfter=6, fontName='Helvetica-Bold', alignment=TA_CENTER)
    stile_normale = ParagraphStyle('normale', fontSize=10.5, spaceAfter=4, fontName='Helvetica', leading=15)
    stile_piccolo = ParagraphStyle('piccolo', fontSize=8, textColor=HexColor("#6b7280"), fontName='Helvetica')

    logo_data = scarica_logo()
    if logo_data:
        logo = Image(logo_data, width=3*cm, height=3*cm)
        logo.hAlign = 'LEFT'
        header_table = Table([[logo, Paragraph(f"<b>{NOME_ASSOCIAZIONE}</b><br/>{CITTA_ASSOCIAZIONE}", stile_titolo)]], colWidths=[4*cm, 13*cm])
        header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (0,0), 'LEFT'), ('ALIGN', (1,0), (1,0), 'CENTER')]))
        elementi.append(header_table)
    else:
        elementi.append(Paragraph(f"<b>{NOME_ASSOCIAZIONE}</b><br/>{CITTA_ASSOCIAZIONE}", stile_titolo))

    elementi.append(Spacer(1, 0.3*cm))
    linea = Table([['']], colWidths=[17*cm], rowHeights=[0.05*cm])
    linea.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), COLORE_PRIMARIO)]))
    elementi.append(linea)
    elementi.append(Spacer(1, 0.8*cm))

    elementi.append(Paragraph(f"RICEVUTA EROGAZIONE LIBERALE N. {numero:04d}", ParagraphStyle('sottotit', fontSize=15, fontName='Helvetica-Bold', textColor=COLORE_PRIMARIO, alignment=TA_CENTER, spaceAfter=4)))
    elementi.append(Paragraph(f"Data: {formatta_data_it(data)}", ParagraphStyle('data', fontSize=10, alignment=TA_CENTER, textColor=HexColor("#6b7280"), spaceAfter=20)))
    elementi.append(Spacer(1, 0.6*cm))

    lettere = importo_in_lettere(importo)
    elementi.append(Paragraph(
        f"Si dichiara di ricevere dal/dalla sig./sig.ra <b>{nome_donatore}</b>, in qualità di sostenitore dell'associazione, "
        f"€ {importo:.2f} (<b>{lettere}</b>) a titolo di <b>erogazione liberale</b>"
        + (f", {causale}" if causale else "") + ".",
        stile_normale
    ))
    elementi.append(Spacer(1, 1*cm))

    elementi.append(Paragraph(
        "<u>Operazione non soggetta ad IVA ai sensi dell'art. 2 comma 3 lett. a) del D.P.R. 633/72</u>",
        ParagraphStyle('nota1', fontSize=9, fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=6)
    ))
    elementi.append(Paragraph(
        "<u>Si rilascia la presente su richiesta dell'interessato per i benefici riconosciuti ai sensi dell'art. 83 del Decreto Legislativo 117/2017.</u>",
        ParagraphStyle('nota2', fontSize=9, fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=20)
    ))

    elementi.append(Spacer(1, 1.5*cm))
    elementi.append(Paragraph("Il Presidente", ParagraphStyle('presid_label', fontSize=9, textColor=HexColor("#6b7280"), alignment=TA_CENTER)))
    elementi.append(Paragraph(f"<b>{PRESIDENTE}</b>", ParagraphStyle('presid', fontSize=11, alignment=TA_CENTER, spaceAfter=4)))
    linea_firma = Table([['']], colWidths=[6*cm], rowHeights=[0.02*cm])
    linea_firma.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), HexColor("#9ca3af")), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    elementi.append(Spacer(1, 0.6*cm))

    elementi.append(Spacer(1, 1.5*cm))
    linea2 = Table([['']], colWidths=[17*cm], rowHeights=[0.05*cm])
    linea2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), HexColor("#e5e7eb"))]))
    elementi.append(linea2)
    elementi.append(Spacer(1, 0.3*cm))
    elementi.append(Paragraph(
        f"Ricevuta generata il {datetime.now().strftime('%d/%m/%Y alle %H:%M')} dal sistema gestionale PGS Juvenilia · {NOME_ASSOCIAZIONE} · {CITTA_ASSOCIAZIONE}",
        stile_piccolo
    ))

    doc.build(elementi)
    buffer.seek(0)
    return buffer


def _dati_intestazione(db: Session, tesserato: Tesserato, causale: str, data_scadenza: str = None):
    """Determina a chi va intestata la ricevuta: al genitore se il tesserato ne ha uno
    collegato (caso tipico di un atleta minorenne), altrimenti al tesserato stesso."""
    nome_intestatario = f"{tesserato.nome} {tesserato.cognome}"
    doc_intestatario = tesserato.codice_fiscale if not tesserato.codice_fiscale.startswith('TEMP_') else None
    if tesserato.genitore_id:
        from app.models.utenti import Genitore
        genitore = db.query(Genitore).filter(Genitore.id == tesserato.genitore_id).first()
        if genitore:
            nome_intestatario = f"{genitore.nome} {genitore.cognome}"
            doc_intestatario = genitore.documento_numero
    mese = estrai_mese_competenza(causale, data_scadenza)
    return nome_intestatario, doc_intestatario, mese


@router.get("/{pagamento_id}/pdf")
def genera_ricevuta(pagamento_id: int, db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    if not pagamento.pagato:
        raise HTTPException(status_code=400, detail="Il pagamento non è ancora stato registrato")
    if not pagamento.emetti_ricevuta:
        raise HTTPException(status_code=400, detail="Questo pagamento è stato registrato senza emissione di ricevuta")

    tesserato = db.query(Tesserato).filter(Tesserato.id == pagamento.tesserato_id).first()
    if not tesserato:
        raise HTTPException(status_code=404, detail="Tesserato non trovato")

    tariffa = db.query(Tariffa).filter(Tariffa.id == pagamento.tariffa_id).first()
    causale = pagamento.descrizione or (tariffa.nome if tariffa else "Quota associativa")
    data_pag = pagamento.data_pagamento or datetime.now().strftime("%Y-%m-%d")
    metodo = pagamento.metodo.value if pagamento.metodo else "contanti"
    nome_intest, doc_intest, mese = _dati_intestazione(db, tesserato, causale, str(pagamento.data_scadenza))

    if not pagamento.numero_ricevuta:
        massimo = db.query(Pagamento.numero_ricevuta).filter(Pagamento.numero_ricevuta.isnot(None)).order_by(Pagamento.numero_ricevuta.desc()).first()
        pagamento.numero_ricevuta = (massimo[0] + 1) if massimo and massimo[0] else 1
        db.commit()

    pdf = genera_pdf_ricevuta(
        numero=pagamento.numero_ricevuta,
        tesserato=tesserato,
        importo=pagamento.importo,
        causale=causale,
        data_pagamento=data_pag,
        metodo=metodo,
        intestatario_nome=nome_intest,
        intestatario_doc=doc_intest,
        mese_competenza=mese,
    )

    nome_file = f"ricevuta_{pagamento_id:04d}_{tesserato.cognome}_{tesserato.nome}.pdf"
    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={nome_file}"}
    )


@router.get("/{pagamento_id}/invia-email")
def invia_ricevuta_email(pagamento_id: int, db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    if not pagamento.pagato:
        raise HTTPException(status_code=400, detail="Il pagamento non è stato registrato")
    if not pagamento.emetti_ricevuta:
        raise HTTPException(status_code=400, detail="Questo pagamento è stato registrato senza emissione di ricevuta")

    tesserato = db.query(Tesserato).filter(Tesserato.id == pagamento.tesserato_id).first()
    tariffa = db.query(Tariffa).filter(Tariffa.id == pagamento.tariffa_id).first()
    causale = pagamento.descrizione or (tariffa.nome if tariffa else "Quota associativa")
    data_pag = pagamento.data_pagamento or datetime.now().strftime("%Y-%m-%d")
    metodo = pagamento.metodo.value if pagamento.metodo else "contanti"
    nome_intest, doc_intest, mese = _dati_intestazione(db, tesserato, causale, str(pagamento.data_scadenza))

    if not pagamento.numero_ricevuta:
        massimo = db.query(Pagamento.numero_ricevuta).filter(Pagamento.numero_ricevuta.isnot(None)).order_by(Pagamento.numero_ricevuta.desc()).first()
        pagamento.numero_ricevuta = (massimo[0] + 1) if massimo and massimo[0] else 1
        db.commit()

    email_dest = tesserato.email
    if not email_dest and tesserato.utente_id:
        from app.models.utenti import Utente
        utente_t = db.query(Utente).filter(Utente.id == tesserato.utente_id).first()
        if utente_t:
            email_dest = utente_t.email
    if not email_dest and tesserato.genitore_id:
        from app.models.utenti import Genitore
        genitore = db.query(Genitore).filter(Genitore.id == tesserato.genitore_id).first()
        if genitore and genitore.email:
            email_dest = genitore.email

    if not email_dest:
        raise HTTPException(status_code=400, detail="Il tesserato non ha un indirizzo email")

    pdf = genera_pdf_ricevuta(
        numero=pagamento.numero_ricevuta,
        tesserato=tesserato,
        importo=pagamento.importo,
        causale=causale,
        data_pagamento=data_pag,
        metodo=metodo,
        intestatario_nome=nome_intest,
        intestatario_doc=doc_intest,
        mese_competenza=mese,
    )

    import resend, os, base64
    resend.api_key = os.getenv("RESEND_API_KEY")
    pdf_b64 = base64.b64encode(pdf.read()).decode()

    resend.Emails.send({
        "from": "PGS Juvenilia - Gestionale <onboarding@resend.dev>",
        "to": [email_dest],
        "subject": f"Ricevuta di pagamento N. {pagamento_id:04d} - {NOME_ASSOCIAZIONE}",
        "text": f"Gentile {nome_intest},\n\nIn allegato trovi la ricevuta di pagamento N. {pagamento_id:04d} per € {pagamento.importo:.2f}.\n\nGrazie,\n{NOME_ASSOCIAZIONE}",
        "attachments": [{"filename": f"ricevuta_{pagamento_id:04d}.pdf", "content": pdf_b64}]
    })

    return {"ok": True, "email": email_dest}


# ---- RICEVUTE EROGAZIONE LIBERALE (donazioni) ----

@router.get("/erogazione-liberale/", response_model=list[RicevutaDonazioneRead])
def lista_ricevute_donazione(db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    return db.query(RicevutaDonazione).order_by(RicevutaDonazione.id.desc()).all()


@router.post("/erogazione-liberale/", response_model=RicevutaDonazioneRead)
def crea_ricevuta_donazione(dati: RicevutaDonazioneCreate, db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    db_ricevuta = RicevutaDonazione(**dati.model_dump(), creato_il=datetime.now().date())
    db.add(db_ricevuta)
    db.commit()
    db.refresh(db_ricevuta)
    return db_ricevuta


@router.put("/erogazione-liberale/{ricevuta_id}", response_model=RicevutaDonazioneRead)
def modifica_ricevuta_donazione(ricevuta_id: int, dati: RicevutaDonazioneCreate, db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    db_ricevuta = db.query(RicevutaDonazione).filter(RicevutaDonazione.id == ricevuta_id).first()
    if not db_ricevuta:
        raise HTTPException(status_code=404, detail="Ricevuta non trovata")
    for campo, valore in dati.model_dump().items():
        setattr(db_ricevuta, campo, valore)
    db.commit()
    db.refresh(db_ricevuta)
    return db_ricevuta


@router.delete("/erogazione-liberale/{ricevuta_id}")
def elimina_ricevuta_donazione(ricevuta_id: int, db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    db_ricevuta = db.query(RicevutaDonazione).filter(RicevutaDonazione.id == ricevuta_id).first()
    if not db_ricevuta:
        raise HTTPException(status_code=404, detail="Ricevuta non trovata")
    db.delete(db_ricevuta)
    db.commit()
    return {"messaggio": "Ricevuta eliminata"}


@router.get("/erogazione-liberale/{ricevuta_id}/pdf")
def scarica_ricevuta_donazione(ricevuta_id: int, db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    ricevuta = db.query(RicevutaDonazione).filter(RicevutaDonazione.id == ricevuta_id).first()
    if not ricevuta:
        raise HTTPException(status_code=404, detail="Ricevuta non trovata")
    pdf = genera_pdf_ricevuta_donazione(
        numero=ricevuta.id,
        nome_donatore=ricevuta.nome_donatore,
        importo=float(ricevuta.importo),
        data=str(ricevuta.data),
        causale=ricevuta.causale,
    )
    nome_file = f"ricevuta_donazione_{ricevuta.id:04d}.pdf"
    return StreamingResponse(
        pdf, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={nome_file}"}
    )
