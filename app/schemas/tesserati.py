from pydantic import BaseModel
from datetime import date
from typing import Optional

class TesseratoCreate(BaseModel):
    nome: str
    cognome: str
    data_nascita: date
    codice_fiscale: str
    telefono: Optional[str] = None
    indirizzo: Optional[str] = None
    e_socio: bool = True
    genitore_id: Optional[int] = None

class TesseratoRead(TesseratoCreate):
    id: int
    attivo: bool

    class Config:
        from_attributes = True
