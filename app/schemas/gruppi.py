from pydantic import BaseModel
from typing import Optional

class GruppoCreate(BaseModel):
    nome: str
    descrizione: Optional[str] = None

class GruppoRead(GruppoCreate):
    id: int
    attivo: bool
    num_tesserati: Optional[int] = 0

    class Config:
        from_attributes = True
