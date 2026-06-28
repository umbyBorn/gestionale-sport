from pydantic import BaseModel
from datetime import date, time
from typing import Optional
from enum import Enum

class StatoAssembleaEnum(str, Enum):
    pianificata = "pianificata"
    conclusa = "conclusa"
    annullata = "annullata"

class TipoVotoEnum(str, Enum):
    favorevole = "favorevole"
    contrario = "contrario"
    astenuto = "astenuto"

class AssembleaCreate(BaseModel):
    titolo: str
    data: date
    ora: Optional[time] = None
    luogo: Optional[str] = None
    stato: StatoAssembleaEnum = StatoAssembleaEnum.pianificata
    note: Optional[str] = None

class AssembleaRead(AssembleaCreate):
    id: int
    path_verbale: Optional[str] = None

    class Config:
        from_attributes = True

class PuntoOrdineGiornoCreate(BaseModel):
    assemblea_id: int
    numero: int
    titolo: str
    descrizione: Optional[str] = None
    esito: Optional[str] = None

class PuntoOrdineGiornoRead(PuntoOrdineGiornoCreate):
    id: int

    class Config:
        from_attributes = True

class PartecipazioneCreate(BaseModel):
    assemblea_id: int
    tesserato_id: int
    presente: bool = False
    delega_a_id: Optional[int] = None
    voto: Optional[TipoVotoEnum] = None

class PartecipazioneRead(PartecipazioneCreate):
    id: int

    class Config:
        from_attributes = True
