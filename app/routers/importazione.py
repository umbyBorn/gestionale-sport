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
        df = pd.read_csv(io.BytesIO(contenuto), dtype=str, sep=';', encoding='utf-8-sig')
    elif nome.endswith(".xlsx") or nome.endswith(".xls"):
        df = pd.read_excel(io.BytesIO(contenuto), dtype=str)
    else:
        raise HTTPException(status_code=400, detail="Formato file non supportato. Usa .xlsx, .xls o .csv")
    df.columns = df.columns.str.strip().str.lower()
    return df.fillna("")

def col(row, *nomi):
    for nome in nomi:
        val = str(row.get(nome, "")).strip()
        if val:
            return val
    return None

def parse_data(valore) -> date:
    valore = str(valore).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(valore, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"data non valida: '{valore}' (usa AAAA-MM-GG o GG/MM/AAAA)")

def parse_bool(valore) -> bool:
    return str(valore).strip().upper() in ("SI", "SÌ", "YES", "TRUE", "1")

@router.post("/import/tesserati", response_model=ImportResult)
async def importa_tesserati(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contenuto = await file.read()
    df = leggi_file(file.filename, contenuto)

    richieste = {"nome", "cognome", "data_nascita", "codice fiscale"}
    mancanti = richieste - set(df.columns)
    if mancanti:
        raise HTTPException(status_code=400, detail=f"Colonne mancanti nel file: {', '.join(mancanti)}")

    creati, saltati, errori = 0, 0, []

    for idx, row in df.iterrows():
        riga_num = idx + 2
        try:
            cf = str(row.get("codice fiscale") or row.get("codice_fiscale", "")).strip().upper()
            if not cf:
                raise ValueError("codice fiscale mancante")

            if db.query(Tesserato).filter(Tesserato.codice_fiscale == cf).first():
                saltati += 1
                continue

            nome = col(row, "nome")
            cognome = col(row, "cognome")
            if not nome or not cognome:
                raise ValueError("nome o cognome mancante")

            # Data nascita
            data_nascita_raw = col(row, "data_nascita", "data nascita")
            if not data_nascita_raw:
                raise ValueError("data nascita mancante")

            # Data tessera
            data_emissione = None
            data_scadenza_tessera = None
            try:
                emessa = col(row, "emessa_il", "emessa il")
                if emessa:
                    data_emissione = parse_data(emessa)
            except ValueError:
                pass
            try:
                scade = col(row, "scade_il", "scade il")
                if scade:
                    data_scadenza_tessera = parse_data(scade)
            except ValueError:
                pass

            tesserato = Tesserato(
                nome=nome,
                cognome=cognome,
                data_nascita=parse_data(data_nascita_raw),
                codice_fiscale=cf,
                sesso=col(row, "sesso"),
                email=col(row, "e-mail", "email"),
                telefono=col(row, "telefono"),
                cellulare=col(row, "cell.", "cellulare"),
                comune_nascita=col(row, "comune nascita", "comune_nascita"),
                provincia_nascita=col(row, "prov", "provincia_nascita"),
                stato_nascita=col(row, "stato nascita", "stato_nascita"),
                indirizzo=col(row, "indirizzo res", "indirizzo_res", "indirizzo"),
                comune_residenza=col(row, "comune res.", "comune_residenza"),
                provincia_residenza=col(row, "provincia res.", "provincia_residenza"),
                regione_residenza=col(row, "regione res.", "regione_residenza"),
                cap_residenza=col(row, "cap res.", "cap_residenza"),
                cod_tessera=col(row, "cod_tessera", "cod tessera"),
                tipo_tessera=col(row, "tipo_tessera", "tipo tessera"),
                categoria=col(row, "categoria"),
                qualifica=col(row, "qualifica"),
                sport=col(row, "sport"),
                data_emissione_tessera=data_emissione,
                data_scadenza_tessera=data_scadenza_tessera,
                matricola=col(row, "matricola"),
                disabile=parse_bool(row.get("disabile", "")),
                straniero=parse_bool(row.get("straniero", "")),
                titolo_studio=col(row, "titolo studio", "titolo_studio"),
                e_socio=True,
            )
            db.add(tesserato)
            db.flush()

            gruppo_nome = col(row, "gruppo", "categoria")
            if gruppo_nome:
                gruppo = db.query(Gruppo).filter(Gruppo.nome.ilike(gruppo_nome)).first()
                if gruppo:
                    db.add(GruppoTesserato(
                        gruppo_id=gruppo.id,
                        tesserato_id=tesserato.id,
                        data_iscrizione=date.today()
                    ))
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
                telefono=col(row, "telefono") or None,
                email=col(row, "email") or None,
                ruolo=str(row["ruolo"]).strip(),
                tipo_rapporto=TipoRapportoEnum(tipo_raw),
                data_inizio=parse_data(row["data_inizio"]),
            )
            db.add(staff)
            db.flush()

            gruppo_nome = col(row, "gruppo")
            if gruppo_nome:
                gruppo = db.query(Gruppo).filter(Gruppo.nome.ilike(gruppo_nome)).first()
                if gruppo:
                    db.add(StaffGruppo(gruppo_id=gruppo.id, staff_id=staff.id))
                else:
                    errori.append(RigaErrore(riga=riga_num, errore=f"gruppo '{gruppo_nome}' non trovato, staff creato senza gruppo"))

            creati += 1
        except Exception as e:
            errori.append(RigaErrore(riga=riga_num, errore=str(e)))

    db.commit()
    return ImportResult(creati=creati, saltati=saltati, errori=errori)
