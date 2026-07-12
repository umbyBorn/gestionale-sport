from pydantic import BaseModel
from datetime import date, time
from typing import Optional
from enum import Enum

class TipoEventoEnum(str, Enum):
    allenamento = "allenamento"
    partita = "partita"
    raduno = "raduno"
    altro = "altro"

class EventoCreate(BaseModel):
    gruppo_id: int
    tipo: TipoEventoEnum = TipoEventoEnum.allenamento
    titolo: str
    data: date
    ora_inizio: Optional[time] = None
    ora_fine: Optional[time] = None
    luogo: Optional[str] = None
    note: Optional[str] = None

class EventoRead(EventoCreate):
    id: int
    ricorrente_id: Optional[int] = None

    class Config:
        from_attributes = True

class EventoUpdate(BaseModel):
    gruppo_id: Optional[int] = None
    tipo: Optional[TipoEventoEnum] = None
    titolo: Optional[str] = None
    data: Optional[date] = None
    ora_inizio: Optional[time] = None
    ora_fine: Optional[time] = None
    luogo: Optional[str] = None
    note: Optional[str] = None

class PresenzaCreate(BaseModel):
    evento_id: int
    tesserato_id: int
    presente: bool
    note: Optional[str] = None

class PresenzaRead(PresenzaCreate):
    id: int

    class Config:
        from_attributes = True
