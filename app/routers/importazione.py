from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.utenti import Tesserato, Gruppo, GruppoTesserato
from app.models.staff import Staff, StaffGruppo, TipoRapportoEnum
from app.schemas.importazione import ImportResult, RigaErrore
import pandas as pd
import io
from datetime import date, datetime

router = APIRouter(tags=["Importazione"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def leggi_file(filename: str, contenuto: bytes) -> pd.DataFrame:
    nome = filename.lower()
    if nome.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(contenuto), dtype=str)
    elif nome.endswith(".xlsx") or nome.endswith(".xls"):
        df = pd.read_excel(io.BytesIO(contenuto), dtype=str)
    else:
        raise HTTPException(status_code=400, detail="Formato file non supportato. Usa .xlsx, .xls o .csv")
    df.columns = df.columns.str.strip().str.lower()
    return df.fillna("")

def parse_data(valore) -> date:
    valore = str(valore).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(valore, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"data non valida: '{valore}' (usa AAAA-MM-GG o GG/MM/AAAA)")

@router.post("/import/tesserati", response_model=ImportResult)
async def importa_tesserati(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contenuto = await file.read()
    df = leggi_file(file.filename, contenuto)

    richieste = {"nome", "cognome", "data_nascita", "codice_fiscale"}
    mancanti = richieste - set(df.columns)
    if mancanti:
        raise HTTPException(status_code=400, detail=f"Colonne mancanti nel file: {', '.join(mancanti)}")

    creati, saltati, errori = 0, 0, []

    for idx, row in df.iterrows():
        riga_num = idx + 2
        try:
            cf = str(row["codice_fiscale"]).strip().upper()
            if not cf:
                raise ValueError("codice fiscale mancante")

            if db.query(Tesserato).filter(Tesserato.codice_fiscale == cf).first():
                saltati += 1
                continue

            nome = str(row["nome"]).strip()
            cognome = str(row["cognome"]).strip()
            if not nome or not cognome:
                raise ValueError("nome o cognome mancante")

            genitore_id = None
            genitore_cf = str(row.get("genitore_codice_fiscale", "")).strip().upper()
            if genitore_cf:
                genitore = db.query(Tesserato).filter(Tesserato.codice_fiscale == genitore_cf).first()
                if genitore:
                    genitore_id = genitore.id
                else:
                    errori.append(RigaErrore(riga=riga_num, errore=f"genitore con CF {genitore_cf} non trovato, tesserato creato senza collegamento"))

            tesserato = Tesserato(
                nome=nome,
                cognome=cognome,
                data_nascita=parse_data(row["data_nascita"]),
                codice_fiscale=cf,
                telefono=str(row.get("telefono", "")).strip() or None,
                indirizzo=str(row.get("indirizzo", "")).strip() or None,
                genitore_id=genitore_id,
            )
            db.add(tesserato)
            db.flush()

            gruppo_nome = str(row.get("gruppo", "")).strip()
            if gruppo_nome:
                gruppo = db.query(Gruppo).filter(Gruppo.nome == gruppo_nome).first()
                if gruppo:
                    db.add(GruppoTesserato(gruppo_id=gruppo.id, tesserato_id=tesserato.id, data_iscrizione=date.today()))
                else:
                    errori.append(RigaErrore(riga=riga_num, errore=f"gruppo '{gruppo_nome}' non trovato, tesserato creato senza gruppo"))

            creati += 1
        except Exception as e:
            errori.append(RigaErrore(riga=riga_num, errore=str(e)))

    db.commit()
    return ImportResult(creati=creati, saltati=saltati, errori=errori)

@router.post("/import/staff", response_model=ImportResult)
async def importa_staff(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contenuto = await file.read()
    df = leggi_file(file.filename, contenuto)

    richieste = {"nome", "cognome", "data_nascita", "codice_fiscale", "ruolo", "tipo_rapporto", "data_inizio"}
    mancanti = richieste - set(df.columns)
    if mancanti:
        raise HTTPException(status_code=400, detail=f"Colonne mancanti nel file: {', '.join(mancanti)}")

    creati, saltati, errori = 0, 0, []

    for idx, row in df.iterrows():
        riga_num = idx + 2
        try:
            cf = str(row["codice_fiscale"]).strip().upper()
            if not cf:
                raise ValueError("codice fiscale mancante")

            if db.query(Staff).filter(Staff.codice_fiscale == cf).first():
                saltati += 1
                continue

            tipo_raw = str(row["tipo_rapporto"]).strip().lower()
            if tipo_raw not in TipoRapportoEnum._value2member_map_:
                raise ValueError(f"tipo_rapporto non valido: '{tipo_raw}' (ammessi: volontario, cococo, altro)")

            staff = Staff(
                nome=str(row["nome"]).strip(),
                cognome=str(row["cognome"]).strip(),
                data_nascita=parse_data(row["data_nascita"]),
                codice_fiscale=cf,
                telefono=str(row.get("telefono", "")).strip() or None,
                email=str(row.get("email", "")).strip() or None,
                ruolo=str(row["ruolo"]).strip(),
                tipo_rapporto=TipoRapportoEnum(tipo_raw),
                data_inizio=parse_data(row["data_inizio"]),
            )
            db.add(staff)
            db.flush()

            gruppo_nome = str(row.get("gruppo", "")).strip()
            if gruppo_nome:
                gruppo = db.query(Gruppo).filter(Gruppo.nome == gruppo_nome).first()
                if gruppo:
                    db.add(StaffGruppo(gruppo_id=gruppo.id, staff_id=staff.id))
                else:
                    errori.append(RigaErrore(riga=riga_num, errore=f"gruppo '{gruppo_nome}' non trovato, staff creato senza gruppo"))

            creati += 1
        except Exception as e:
            errori.append(RigaErrore(riga=riga_num, errore=str(e)))

    db.commit()
    return ImportResult(creati=creati, saltati=saltati, errori=errori)
