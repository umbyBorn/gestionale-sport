from pydantic import BaseModel
from datetime import date
from typing import Optional, List
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
    descrizione: Optional[str] = None
    evento_id: Optional[int] = None

class PagamentoUpdate(BaseModel):
    tariffa_id: Optional[int] = None
    importo: Optional[float] = None
    data_scadenza: Optional[date] = None
    data_pagamento: Optional[date] = None
    metodo: Optional[MetodoPagamentoEnum] = None
    pagato: Optional[bool] = None
    descrizione: Optional[str] = None
    evento_id: Optional[int] = None

class PagamentoRead(PagamentoCreate):
    id: int
    contabile_allegata: Optional[str] = None
    gruppo_generazione_id: Optional[str] = None

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


# ---- GENERAZIONE SCADENZE AUTOMATICHE ----

class VoceScadenza(BaseModel):
    """Una singola voce dello scadenzario da generare (es. Iscrizione, Settembre, Ottobre...)"""
    nome: str
    importo: float
    data_scadenza: date

class PianoScadenzeCreate(BaseModel):
    # destinatari: uno tra tesserato_ids o gruppo_id deve essere fornito
    tesserato_ids: Optional[List[int]] = None
    gruppo_id: Optional[int] = None
    voci: List[VoceScadenza]
    categoria_tariffa: Optional[str] = "Quote associative"

class PianoScadenzeResult(BaseModel):
    tesserati_coinvolti: int
    pagamenti_creati: int
    gruppo_generazione_id: str


# ---- PAGAMENTI DI GRUPPO (ad hoc: completino, gita, torneo...) ----

class PagamentoGruppoCreate(BaseModel):
    tesserato_ids: Optional[List[int]] = None
    gruppo_id: Optional[int] = None
    nome: str  # es. "Completino", "Gita di Natale"
    importo: float
    data_scadenza: date
    evento_id: Optional[int] = None

class PagamentoGruppoResult(BaseModel):
    tesserati_coinvolti: int
    pagamenti_creati: int
    gruppo_generazione_id: str


# ---- PRIMA NOTA ----

class TipoMovimentoEnum(str, Enum):
    entrata = "entrata"
    uscita = "uscita"

class MovimentoContabileCreate(BaseModel):
    tipo: TipoMovimentoEnum
    data: date
    importo: float
    descrizione: str
    categoria: Optional[str] = None
    centro_costo: Optional[str] = None
    intestatario: Optional[str] = None
    allegato: Optional[str] = None
    note: Optional[str] = None

class MovimentoContabileRead(MovimentoContabileCreate):
    id: int
    pagamento_id: Optional[int] = None

    class Config:
        from_attributes = True


# ---- RENDICONTO ----

class RendicontoRigaCategoria(BaseModel):
    categoria: str
    entrate: float
    uscite: float

class RendicontoRigaMensile(BaseModel):
    mese: str  # "2026-09"
    entrate: float
    uscite: float
    saldo: float

class RendicontoResponse(BaseModel):
    periodo_da: date
    periodo_a: date
    totale_entrate: float
    totale_uscite: float
    saldo: float
    per_categoria: List[RendicontoRigaCategoria]
    per_mese: List[RendicontoRigaMensile]


# ---- RICEVUTE EROGAZIONE LIBERALE ----

class RicevutaDonazioneCreate(BaseModel):
    nome_donatore: str
    importo: float
    data: date
    causale: Optional[str] = None

class RicevutaDonazioneRead(RicevutaDonazioneCreate):
    id: int
    creato_il: date

    class Config:
        from_attributes = True
