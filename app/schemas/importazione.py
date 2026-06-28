from pydantic import BaseModel
from typing import List

class RigaErrore(BaseModel):
    riga: int
    errore: str

class ImportResult(BaseModel):
    creati: int
    saltati: int
    errori: List[RigaErrore]
