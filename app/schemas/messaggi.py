from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class MessaggioCreate(BaseModel):
    intestazione: str
    corpo: str
    gruppi_id: List[int] = []
    tesserati_esclusi_id: List[int] = []
    tesserati_aggiuntivi_id: List[int] = []


class DestinatarioRead(BaseModel):
    tesserato_id: int
    nome: str
    cognome: str
    email_inviata: bool

    class Config:
        from_attributes = True


class MessaggioRead(BaseModel):
    id: int
    intestazione: str
    corpo: str
    data_invio: datetime
    destinatari: List[DestinatarioRead] = []

    class Config:
        from_attributes = True
