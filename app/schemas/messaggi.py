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
    email_inviata: bool
    nome: Optional[str] = None
    cognome: Optional[str] = None

    class Config:
        from_attributes = True


class MessaggioRead(BaseModel):
    id: int
    intestazione: str
    corpo: str
    data_invio: datetime
    num_destinatari: Optional[int] = 0
    num_email_inviate: Optional[int] = 0

    class Config:
        from_attributes = True
