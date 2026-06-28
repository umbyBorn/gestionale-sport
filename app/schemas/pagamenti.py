from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum

class MetodoPagamentoEnum(str, Enum):
    contanti = "contanti"
    bonifico = "bonifico"
    altro = "altro"

class PagamentoCreate(BaseModel):
    tesserato_id: int
    tariffa_id: int
    importo: float
    data_scadenza: date
    data_pagamento: Optional[date] = None
    metodo: Optional[MetodoPagamentoEnum] = None
    pagato: bool = False

class PagamentoRead(PagamentoCreate):
    id: int
    contabile_allegata: Optional[str] = None

    class Config:
        from_attributes = True

class TariffaCreate(BaseModel):
    nome: str
    importo: float
    categoria: Optional[str] = None

class TariffaRead(TariffaCreate):
    id: int
    attiva: bool

    class Config:
        from_attributes = True
