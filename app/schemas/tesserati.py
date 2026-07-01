from pydantic import BaseModel
from datetime import date
from typing import Optional


class GenitoreCreate(BaseModel):
    nome: str
    cognome: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    documento_tipo: Optional[str] = None
    documento_numero: Optional[str] = None


class GenitoreRead(GenitoreCreate):
    id: int

    class Config:
        from_attributes = True


class DocumentoCreate(BaseModel):
    tesserato_id: int
    tipo: str
    nome_file: str
    url: str
    data_scadenza: Optional[date] = None
    note: Optional[str] = None


class DocumentoRead(DocumentoCreate):
    id: int

    class Config:
        from_attributes = True


class TesseratoCreate(BaseModel):
    nome: str
    cognome: str
    data_nascita: date
    codice_fiscale: str
    sesso: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    cellulare: Optional[str] = None
    comune_nascita: Optional[str] = None
    provincia_nascita: Optional[str] = None
    stato_nascita: Optional[str] = None
    indirizzo: Optional[str] = None
    comune_residenza: Optional[str] = None
    provincia_residenza: Optional[str] = None
    regione_residenza: Optional[str] = None
    cap_residenza: Optional[str] = None
    cod_tessera: Optional[str] = None
    tipo_tessera: Optional[str] = None
    categoria: Optional[str] = None
    qualifica: Optional[str] = None
    sport: Optional[str] = None
    data_emissione_tessera: Optional[date] = None
    data_scadenza_tessera: Optional[date] = None
    matricola: Optional[str] = None
    disabile: Optional[bool] = False
    straniero: Optional[bool] = False
    titolo_studio: Optional[str] = None
    e_socio: bool = True
    genitore_id: Optional[int] = None
    foto_url: Optional[str] = None


class TesseratoRead(TesseratoCreate):
    id: int
    attivo: bool
    genitore: Optional[GenitoreRead] = None
    documenti: Optional[list[DocumentoRead]] = []

    class Config:
        from_attributes = True
