from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum

class TipoRapportoEnum(str, Enum):
    volontario = "volontario"
    cococo = "cococo"
    altro = "altro"

class TipoContrattoEnum(str, Enum):
    sportivo = "sportivo"
    amministrativo = "amministrativo"

class StaffCreate(BaseModel):
    nome: str
    cognome: str
    data_nascita: date
    codice_fiscale: str
    indirizzo: Optional[str] = None
    comune_residenza: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    ruolo: str
    tipo_rapporto: TipoRapportoEnum
    data_inizio: date
    data_fine: Optional[date] = None
    numero_tessera: Optional[int] = None
    data_emissione_tessera: Optional[date] = None
    quota_associativa: Optional[float] = 5
    quota_pagata: Optional[bool] = False
    tesserato_origine_id: Optional[int] = None

class StaffRead(StaffCreate):
    id: int
    attivo: bool
    path_modulo_firmato: Optional[str] = None

    class Config:
        from_attributes = True

class CompensoCreate(BaseModel):
    staff_id: int
    importo: float
    data_erogazione: date
    descrizione: Optional[str] = None

class CompensoRead(CompensoCreate):
    id: int
    totale_progressivo: float
    soglia_superata: bool

    class Config:
        from_attributes = True

class ContrattoCreate(BaseModel):
    staff_id: int
    tipo: TipoContrattoEnum
    data_inizio: date
    data_fine: Optional[date] = None
    importo: float
    firmato: bool = False

class ContrattoRead(ContrattoCreate):
    id: int
    path_pdf: Optional[str] = None

    class Config:
        from_attributes = True
