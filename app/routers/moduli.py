"""
Generazione di moduli PDF precompilati con i dati del tesserato (e del genitore/tutore
se il tesserato è minorenne): Modulo di Adesione all'associazione e Lettera di
Tesseramento. I moduli vengono generati già compilati con i dati anagrafici noti al
gestionale, pronti per la stampa e la firma manuale (che resta necessariamente cartacea).
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.utenti import Tesserato, Genitore
from app.auth import get_utente_corrente
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io

router = APIRouter(prefix="/moduli", tags=["Moduli"])

NOME_ASSOCIAZIONE = "ASD P.G.S. JUVENILIA"
CF_ASSOCIAZIONE = "93162560879"
CITTA_ASSOCIAZIONE = "Catania"
PRESIDENTE = "Sardo Carmela Linda"
COLORE_PRIMARIO = HexColor("#1e3a8a")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _dati_richiedente(db: Session, tesserato: Tesserato):
    """Se il tesserato ha un genitore/tutore collegato (caso tipico dei minorenni),
    il modulo va compilato con i dati del genitore come richiedente, indicando
    il minore come tale. Altrimenti il richiedente è il tesserato stesso."""
    genitore = None
    if tesserato.genitore_id:
        genitore = db.query(Genitore).filter(Genitore.id == tesserato.genitore_id).first()
    return genitore


def _formatta_data(d) -> str:
    if not d:
        return "___________________"
    return d.strftime("%d/%m/%Y")


def _intestazione_richiedente(elementi, stile_campo, tesserato: Tesserato, genitore):
    """Blocco 'Il/la sottoscritto/a ...' — con i dati del genitore se presente,
    altrimenti quelli del tesserato stesso."""
    if genitore:
        nome = f"{genitore.nome} {genitore.cognome}"
        cf = genitore.documento_numero or "___________________"
        indirizzo = tesserato.indirizzo or "___________________"
        comune = tesserato.comune_residenza or "___________________"
        provincia = tesserato.provincia_residenza or "___"
        email = genitore.email or "___________________"
        telefono = genitore.telefono or "___________________"
    else:
        nome = f"{tesserato.nome} {tesserato.cognome}"
        cf = tesserato.codice_fiscale if not tesserato.codice_fiscale.startswith("TEMP_") else "___________________"
        indirizzo = tesserato.indirizzo or "___________________"
        comune = tesserato.comune_residenza or "___________________"
        provincia = tesserato.provincia_residenza or "___"
        email = tesserato.email or "___________________"
        telefono = tesserato.cellulare or tesserato.telefono or "___________________"

    elementi.append(Paragraph(f"Il/la sottoscritto/a <b>{nome}</b>", stile_campo))
    elementi.append(Paragraph(f"Codice Fiscale: <b>{cf}</b>", stile_campo))
    elementi.append(Paragraph(f"Residente in <b>{comune}</b> ({provincia}), Via/Indirizzo: <b>{indirizzo}</b>", stile_campo))
    elementi.append(Paragraph(f"Email: <b>{email}</b> — Cellulare: <b>{telefono}</b>", stile_campo))

    if genitore:
        elementi.append(Spacer(1, 0.3*cm))
        elementi.append(Paragraph(
            f"In qualità di genitore/tutore di <b>{tesserato.nome} {tesserato.cognome}</b>, "
            f"nato/a a <b>{tesserato.comune_nascita or '___________'}</b> il "
            f"<b>{_formatta_data(tesserato.data_nascita)}</b>, "
            f"C.F.: <b>{tesserato.codice_fiscale if not tesserato.codice_fiscale.startswith('TEMP_') else '___________________'}</b>.",
            stile_campo
        ))


def _intestazione_pdf(elementi, titolo: str, stile_titolo, stile_sub):
    elementi.append(Paragraph(NOME_ASSOCIAZIONE, stile_sub))
    elementi.append(Paragraph(f"Codice Fiscale {CF_ASSOCIAZIONE} — Sede: {CITTA_ASSOCIAZIONE}", ParagraphStyle('sede', fontSize=9, textColor=HexColor("#6b7280"), alignment=TA_CENTER, spaceAfter=16)))
    elementi.append(Paragraph(titolo, stile_titolo))
    elementi.append(Spacer(1, 0.6*cm))


def genera_pdf_adesione(tesserato: Tesserato, genitore) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2.2*cm, leftMargin=2.2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elementi = []

    stile_titolo = ParagraphStyle('titolo', fontSize=13, fontName='Helvetica-Bold', textColor=COLORE_PRIMARIO, alignment=TA_CENTER, spaceAfter=4, leading=17)
    stile_sub = ParagraphStyle('sub', fontSize=11, fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=2)
    stile_campo = ParagraphStyle('campo', fontSize=10, fontName='Helvetica', spaceAfter=6, leading=14)
    stile_corpo = ParagraphStyle('corpo', fontSize=9.5, fontName='Helvetica', alignment=TA_JUSTIFY, spaceAfter=6, leading=13)
    stile_firma = ParagraphStyle('firma', fontSize=10, fontName='Helvetica', spaceAfter=4)

    _intestazione_pdf(elementi, f"MODULO DI RICHIESTA ADESIONE ASSOCIAZIONE SPORTIVA<br/>\u201c{NOME_ASSOCIAZIONE}\u201d", stile_titolo, stile_sub)

    elementi.append(Paragraph(f"Al Consiglio Direttivo dell'Associazione Sportiva \u201c{NOME_ASSOCIAZIONE}\u201d, Codice Fiscale {CF_ASSOCIAZIONE}", stile_campo))
    elementi.append(Spacer(1, 0.3*cm))

    _intestazione_richiedente(elementi, stile_campo, tesserato, genitore)
    elementi.append(Spacer(1, 0.4*cm))

    elementi.append(Paragraph("Avendo preso visione dello Statuto dell'Associazione", stile_campo))
    elementi.append(Paragraph("<b>CHIEDE</b>", ParagraphStyle('chiede', fontSize=11, fontName='Helvetica-Bold', spaceAfter=6)))
    elementi.append(Paragraph(
        f"Di poter aderire all'associazione sportiva \u201c{NOME_ASSOCIAZIONE}\u201d in qualità di Socio Ordinario. "
        f"A tal fine effettua il versamento della quota associativa annuale pari a ___________ euro.",
        stile_corpo
    ))
    elementi.append(Paragraph(
        "Dichiara di aver letto lo statuto e di attenersi ad eventuali regolamenti dell'Associazione oltre che "
        "alle deliberazioni adottate dagli organi sociali.",
        stile_corpo
    ))
    elementi.append(Spacer(1, 0.4*cm))
    elementi.append(Paragraph(f"Luogo e data: {CITTA_ASSOCIAZIONE}, ___________________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Firma: ___________________________", stile_firma))
    elementi.append(Spacer(1, 0.5*cm))

    elementi.append(Paragraph("A tal scopo dichiara:", ParagraphStyle('scopo', fontSize=10, fontName='Helvetica-Bold', spaceAfter=6)))
    punti_a = [
        "Di condividere le finalità dello Statuto e di voler contribuire, secondo le proprie capacità e disponibilità "
        "di tempo e mezzi, alla loro realizzazione;",
        "Che verserà la quota associativa annuale, secondo le modalità stabilite dal Consiglio Direttivo;",
        "Di autorizzare ☐ o non autorizzare ☐ l'Associazione all'utilizzo di foto scattate e/o riprese video effettuate "
        "durante eventi e manifestazioni organizzati dall'Associazione stessa, limitatamente a: pubblicazioni sul sito "
        "dell'Associazione, stampa materiale pubblicitario a cura dell'Associazione, pubblicazione sulla stampa periodica locale;",
    ]
    for i, testo in enumerate(punti_a):
        lettera = chr(ord('a') + i)
        elementi.append(Paragraph(f"{lettera}) {testo}", stile_corpo))

    elementi.append(Paragraph("inoltre:", stile_campo))
    punti_b = [
        f"Si impegna a non utilizzare il nome dell'Associazione \u201c{NOME_ASSOCIAZIONE}\u201d e il materiale da essa "
        "prodotto ai fini associativi, per attività di carattere commerciale, imprenditoriale o, in ogni caso, aventi scopo di lucro;",
        "Prende atto che l'adesione come Socio sostenitore è subordinata all'accettazione, da parte del Consiglio Direttivo, "
        "come previsto dall'art. 5 dello Statuto;",
        "In qualità di Socio acquisirà i diritti e i doveri previsti dagli art. 6 e 7 dello Statuto.",
    ]
    for i, testo in enumerate(punti_b):
        lettera = chr(ord('a') + i)
        elementi.append(Paragraph(f"{lettera}) {testo}", stile_corpo))

    elementi.append(Spacer(1, 0.3*cm))
    elementi.append(Paragraph(f"Luogo e data: {CITTA_ASSOCIAZIONE}, ___________________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Firma: ___________________________", stile_firma))
    elementi.append(Spacer(1, 0.6*cm))

    elementi.append(Paragraph(
        "<b>Consenso al trattamento dei dati personali</b> ai sensi dell'art. 23 D.lgs. 196 del 30/6/2003",
        ParagraphStyle('consenso_tit', fontSize=10, fontName='Helvetica-Bold', spaceAfter=6)
    ))
    elementi.append(Paragraph(
        f"I dati forniti, da chi presenta richiesta di adesione, vengono registrati nel libro soci e/o in appositi registri, "
        f"predisposti su supporto cartaceo e/o elettronico dall'Associazione \u201c{NOME_ASSOCIAZIONE}\u201d, con sede in "
        f"{CITTA_ASSOCIAZIONE}, che ne è responsabile per il trattamento. Per dati si intendono quelli forniti durante la "
        "registrazione quale associato e le successive modifiche e/o integrazioni da parte dell'associato stesso. "
        "In conformità con l'art. 13 del D.lgs 30 giugno 2003, recante il Codice in materia di protezione dei dati "
        "personali, si desidera informare il socio che i dati personali volontariamente forniti per aderire "
        "all'Associazione suddetta, saranno trattati, da parte dell'Associazione stessa, adottando tutte le misure "
        "idonee a garantire la sicurezza e la riservatezza nel rispetto della normativa sopra richiamata. Il consenso "
        "al trattamento dei dati personali viene fornito con la richiesta di adesione; in assenza del consenso non è "
        "possibile aderire all'Associazione, né fruire dei suoi servizi. L'indicazione di nome, data di nascita e "
        "recapiti (indirizzo, telefono e mail) è necessaria per la gestione del rapporto associativo e per "
        "l'adempimento degli obblighi di legge. Il conferimento degli altri dati è facoltativo. L'interessato può, "
        "in qualsiasi momento, decidere quali dati (non obbligatori) lasciare nella disponibilità dell'Associazione "
        "e quali informazioni ricevere.",
        stile_corpo
    ))
    elementi.append(Paragraph(
        f"Titolare del trattamento è l'Associazione \u201c{NOME_ASSOCIAZIONE}\u201d, con sede a {CITTA_ASSOCIAZIONE}. "
        f"Responsabile del trattamento è il Presidente, {PRESIDENTE}.",
        stile_corpo
    ))
    elementi.append(Paragraph(
        "Il/La sottoscritto/a, ricevuta l'informativa ai sensi dell'art. 13 del D.lgs. 196/2003, dà il consenso al "
        "trattamento dei propri dati personali nella misura necessaria al raggiungimento degli scopi statutari e con "
        "le modalità indicate nell'informativa medesima.",
        stile_corpo
    ))
    elementi.append(Spacer(1, 0.4*cm))
    elementi.append(Paragraph(f"Luogo e data: {CITTA_ASSOCIAZIONE}, ___________________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Firma: ___________________________", stile_firma))

    doc.build(elementi)
    buffer.seek(0)
    return buffer


def genera_pdf_tesseramento(tesserato: Tesserato, genitore) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2.2*cm, leftMargin=2.2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elementi = []

    stile_titolo = ParagraphStyle('titolo', fontSize=15, fontName='Helvetica-Bold', textColor=COLORE_PRIMARIO, alignment=TA_CENTER, spaceAfter=14)
    stile_campo = ParagraphStyle('campo', fontSize=10, fontName='Helvetica', spaceAfter=6, leading=14)
    stile_corpo = ParagraphStyle('corpo', fontSize=9.5, fontName='Helvetica', alignment=TA_JUSTIFY, spaceAfter=6, leading=13)
    stile_sezione = ParagraphStyle('sezione', fontSize=10.5, fontName='Helvetica-Bold', spaceAfter=6, spaceBefore=10)
    stile_firma = ParagraphStyle('firma', fontSize=10, fontName='Helvetica', spaceAfter=4)

    elementi.append(Paragraph("LETTERA DI TESSERAMENTO", stile_titolo))

    _intestazione_richiedente(elementi, stile_campo, tesserato, genitore)
    elementi.append(Spacer(1, 0.4*cm))

    elementi.append(Paragraph("<b>CHIEDE</b>", ParagraphStyle('chiede', fontSize=11, fontName='Helvetica-Bold', spaceAfter=6)))
    elementi.append(Paragraph(
        f"di essere ammesso in qualità di tesserato, ai sensi degli artt. 15 e 16 del D.Lgs. 36/2021 alla {NOME_ASSOCIAZIONE} "
        "e dichiara di accettare e seguire i seguenti regolamenti:",
        stile_corpo
    ))

    sezioni = [
        ("1) RESPONSABILITÀ", [
            "nessuna responsabilità potrà essere addebitata alla associazione per eventuali danni che dovessero derivare "
            "direttamente o indirettamente dalla pratica sportiva svolta nei locali dell'associazione e nei locali che "
            "ospitano l'associazione. Esonera, pertanto, l'associazione da qualsiasi responsabilità per danni alla persona "
            "sua o d'altri, così come a cose proprie o altrui, che possono derivare dalla partecipazione alle attività "
            "associative sia in luoghi al chiuso che all'aperto.",
            "gli allenamenti liberi, l'uso di attrezzature sportive personali o della associazione sono severamente "
            "proibiti senza il permesso e l'assistenza di un responsabile.",
            "chi arrecasse con la propria incuria, volontariamente o involontariamente danno alle attrezzature o ai beni "
            "dell'associazione, o ai beni di terzi di cui gode l'associazione per le attività associative dovrà "
            "risarcire la associazione del danno provocato.",
            "l'associazione non risponde del furto o del danno di qualsiasi oggetto personale che dovesse avvenire nei "
            "luoghi ove vengono svolte le attività associative.",
            "nel caso dei bambini, il genitore è a conoscenza che l'associazione non si assume alcuna responsabilità per "
            "quanto possa accadere fuori del luogo e dell'ora delle attività associative, quando i bambini non sono "
            "sotto il controllo diretto del responsabile.",
        ]),
        ("2) ASSICURAZIONE", [
            "l'assicurazione per la pratica sportiva svolta in associazione è coperta da una speciale polizza di "
            "responsabilità civile e dal tesseramento alle federazioni nazionali ed enti di promozione sportiva.",
            "gli associati ed i tesserati devono segnalare immediatamente alla segreteria qualsiasi incidente o danno "
            "accusato durante gli allenamenti per potere procedere alle formalità assicurative.",
        ]),
        ("3) CERTIFICATI MEDICI", [
            "gli associati e i tesserati prima di frequentare i corsi sportivi dovranno presentare obbligatoriamente un "
            "certificato medico di idoneità alla pratica sportiva non agonistica/agonistica secondo le leggi vigenti.",
        ]),
        ("4) REGOLE DI COMPORTAMENTO", [
            "è vietato fumare in associazione.",
            "è vietato agli associati e ai tesserati accedere nelle sale della associazione con le scarpe.",
            "è vietato introdurre nei luoghi ove vengono svolte le attività associative oggetti personali ingombranti, "
            "animali, ecc.",
            "il comportamento nei luoghi ove vengono svolte le attività associative deve essere irreprensibile. Sono "
            "vietati grida o schiamazzi di alcun genere.",
            "non si è autorizzati ad usare in modo improprio le attrezzature e gli altri beni utilizzati per le "
            "attività associative.",
        ]),
    ]
    for titolo_sezione, punti in sezioni:
        elementi.append(Paragraph(titolo_sezione, stile_sezione))
        for i, testo in enumerate(punti):
            lettera = chr(ord('a') + i)
            elementi.append(Paragraph(f"{lettera}) {testo}", stile_corpo))

    elementi.append(Paragraph(
        "La mancata osservanza di una delle precedenti condizioni di associazione può comportare ad insindacabile "
        "giudizio dell'associazione l'espulsione dai locali sociali e dalla associazione.",
        stile_corpo
    ))

    elementi.append(Paragraph("5) FORO COMPETENTE", stile_sezione))
    elementi.append(Paragraph(f"Per ogni eventuale controversia sarà competente il foro di {CITTA_ASSOCIAZIONE}.", stile_corpo))

    elementi.append(Spacer(1, 0.4*cm))
    elementi.append(Paragraph("La presente domanda viene letta, approvata e sottoscritta.", stile_corpo))
    elementi.append(Paragraph(
        "Si approvano specificatamente ai sensi e per gli effetti degli articoli 1341 e 1342 del codice civile le "
        "clausole 1, 2, 3, 4, 5.",
        stile_corpo
    ))
    elementi.append(Spacer(1, 0.5*cm))
    elementi.append(Paragraph(f"Data: ___________________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Firma: ___________________________", stile_firma))

    doc.build(elementi)
    buffer.seek(0)
    return buffer


@router.get("/adesione/{tesserato_id}/pdf")
def scarica_modulo_adesione(tesserato_id: int, db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    tesserato = db.query(Tesserato).filter(Tesserato.id == tesserato_id).first()
    if not tesserato:
        raise HTTPException(status_code=404, detail="Tesserato non trovato")
    genitore = _dati_richiedente(db, tesserato)
    pdf = genera_pdf_adesione(tesserato, genitore)
    return StreamingResponse(
        pdf, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=adesione_{tesserato.cognome}_{tesserato.nome}.pdf"}
    )


@router.get("/tesseramento/{tesserato_id}/pdf")
def scarica_modulo_tesseramento(tesserato_id: int, db: Session = Depends(get_db), utente=Depends(get_utente_corrente)):
    tesserato = db.query(Tesserato).filter(Tesserato.id == tesserato_id).first()
    if not tesserato:
        raise HTTPException(status_code=404, detail="Tesserato non trovato")
    genitore = _dati_richiedente(db, tesserato)
    pdf = genera_pdf_tesseramento(tesserato, genitore)
    return StreamingResponse(
        pdf, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=tesseramento_{tesserato.cognome}_{tesserato.nome}.pdf"}
    )
