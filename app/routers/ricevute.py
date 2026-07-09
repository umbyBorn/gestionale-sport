from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.utenti import Tesserato
from app.models.contabilita import Pagamento, Tariffa
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

router = APIRouter(prefix="/ricevute", tags=["Ricevute"])

NOME_ASSOCIAZIONE = "ASD PGS Juvenilia"
CITTA_ASSOCIAZIONE = "Catania"
PRESIDENTE = "Sardo Carmela Linda"
LOGO_URL = "https://res.cloudinary.com/srjdjqvl/image/upload/v1783538588/logo2_gijh4j.jpg"
COLORE_PRIMARIO = HexColor("#1e3a8a")
COLORE_SECONDARIO = HexColor("#dc2626")

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
    elementi.append(Paragraph(
        f"Data: {data_pagamento}",
        ParagraphStyle('data', fontSize=10, alignment=TA_CENTER, textColor=HexColor("#6b7280"), fontName='Helvetica')
    ))
    elementi.append(Spacer(1, 0.8*cm))

    # BOX DATI TESSERATO
    nome_completo = f"{tesserato.nome} {tesserato.cognome}"
    cf = tesserato.codice_fiscale if not tesserato.codice_fiscale.startswith('TEMP_') else '—'
    indirizzo = tesserato.indirizzo or '—'
    comune = f"{tesserato.comune_residenza or ''} {tesserato.provincia_residenza or ''}".strip() or '—'

    dati_box = [
        [Paragraph('<b>INTESTATARIO</b>', ParagraphStyle('label', fontSize=8, textColor=white, fontName='Helvetica-Bold')), ''],
        [Paragraph(f'<b>{nome_completo}</b>', ParagraphStyle('nome', fontSize=13, textColor=COLORE_PRIMARIO, fontName='Helvetica-Bold')), ''],
        [Paragraph(f'Codice Fiscale: {cf}', stile_normale), Paragraph(f'Indirizzo: {indirizzo}', stile_normale)],
        [Paragraph(f'Comune: {comune}', stile_normale), ''],
    ]

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
        [Paragraph('Il Presidente', ParagraphStyle('firma_label', fontSize=9, textColor=HexColor("#6b7280"), fontName='Helvetica', alignment=TA_CENTER)), ''],
        [Paragraph(f'<b>{PRESIDENTE}</b>', ParagraphStyle('firma_nome', fontSize=11, fontName='Helvetica-Bold', alignment=TA_CENTER)), ''],
        [Paragraph('_________________________', ParagraphStyle('firma_linea', fontSize=11, alignment=TA_CENTER, textColor=HexColor("#9ca3af"))), ''],
    ]
    firma_table = Table(firma_data, colWidths=[8.5*cm, 8.5*cm])
    firma_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
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
        f"Ricevuta generata il {datetime.now().strftime('%d/%m/%Y alle %H:%M')} dal sistema gestionale Golè · {NOME_ASSOCIAZIONE} · {CITTA_ASSOCIAZIONE}",
        stile_piccolo
    ))

    doc.build(elementi)
    buffer.seek(0)
    return buffer


@router.get("/{pagamento_id}/pdf")
def genera_ricevuta(pagamento_id: int, db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    if not pagamento.pagato:
        raise HTTPException(status_code=400, detail="Il pagamento non è ancora stato registrato")

    tesserato = db.query(Tesserato).filter(Tesserato.id == pagamento.tesserato_id).first()
    if not tesserato:
        raise HTTPException(status_code=404, detail="Tesserato non trovato")

    tariffa = db.query(Tariffa).filter(Tariffa.id == pagamento.tariffa_id).first()
    causale = tariffa.nome if tariffa else "Quota associativa"
    data_pag = pagamento.data_pagamento or datetime.now().strftime("%Y-%m-%d")
    metodo = pagamento.metodo.value if pagamento.metodo else "contanti"

    pdf = genera_pdf_ricevuta(
        numero=pagamento_id,
        tesserato=tesserato,
        importo=pagamento.importo,
        causale=causale,
        data_pagamento=data_pag,
        metodo=metodo,
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

    tesserato = db.query(Tesserato).filter(Tesserato.id == pagamento.tesserato_id).first()
    tariffa = db.query(Tariffa).filter(Tariffa.id == pagamento.tariffa_id).first()
    causale = tariffa.nome if tariffa else "Quota associativa"
    data_pag = pagamento.data_pagamento or datetime.now().strftime("%Y-%m-%d")
    metodo = pagamento.metodo.value if pagamento.metodo else "contanti"

    email_dest = tesserato.email
    if not email_dest and tesserato.utente_id:
        from app.models.utenti import Utente
        utente_t = db.query(Utente).filter(Utente.id == tesserato.utente_id).first()
        if utente_t:
            email_dest = utente_t.email

    if not email_dest:
        raise HTTPException(status_code=400, detail="Il tesserato non ha un indirizzo email")

    pdf = genera_pdf_ricevuta(
        numero=pagamento_id,
        tesserato=tesserato,
        importo=pagamento.importo,
        causale=causale,
        data_pagamento=data_pag,
        metodo=metodo,
    )

    import resend, os, base64
    resend.api_key = os.getenv("RESEND_API_KEY")
    pdf_b64 = base64.b64encode(pdf.read()).decode()

    resend.Emails.send({
        "from": "Golè Gestionale <onboarding@resend.dev>",
        "to": [email_dest],
        "subject": f"Ricevuta di pagamento N. {pagamento_id:04d} - {NOME_ASSOCIAZIONE}",
        "text": f"Gentile {tesserato.nome} {tesserato.cognome},\n\nIn allegato trovi la ricevuta di pagamento N. {pagamento_id:04d} per € {pagamento.importo:.2f}.\n\nGrazie,\n{NOME_ASSOCIAZIONE}",
        "attachments": [{"filename": f"ricevuta_{pagamento_id:04d}.pdf", "content": pdf_b64}]
    })

    return {"ok": True, "email": email_dest}
