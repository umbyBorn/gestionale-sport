from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.contabilita import Pagamento, Tariffa
from app.schemas.pagamenti import PagamentoCreate, PagamentoRead, TariffaCreate, TariffaRead, MetodoPagamentoEnum
from typing import List
from datetime import date

router = APIRouter(tags=["Pagamenti"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- TARIFFE ----

@router.get("/tariffe/", response_model=List[TariffaRead])
def lista_tariffe(db: Session = Depends(get_db)):
    return db.query(Tariffa).filter(Tariffa.attiva == True).all()

@router.post("/tariffe/", response_model=TariffaRead)
def crea_tariffa(tariffa: TariffaCreate, db: Session = Depends(get_db)):
    db_tariffa = Tariffa(**tariffa.model_dump())
    db.add(db_tariffa)
    db.commit()
    db.refresh(db_tariffa)
    return db_tariffa

@router.delete("/tariffe/{tariffa_id}")
def elimina_tariffa(tariffa_id: int, db: Session = Depends(get_db)):
    db_tariffa = db.query(Tariffa).filter(Tariffa.id == tariffa_id).first()
    if not db_tariffa:
        raise HTTPException(status_code=404, detail="Tariffa non trovata")
    db_tariffa.attiva = False
    db.commit()
    return {"messaggio": "Tariffa disattivata"}

# ---- PAGAMENTI ----

@router.get("/pagamenti/", response_model=List[PagamentoRead])
def lista_pagamenti(db: Session = Depends(get_db)):
    return db.query(Pagamento).all()

@router.get("/pagamenti/scaduti/", response_model=List[PagamentoRead])
def pagamenti_scaduti(db: Session = Depends(get_db)):
    return db.query(Pagamento).filter(
        Pagamento.pagato == False,
        Pagamento.data_scadenza < date.today()
    ).all()

@router.get("/pagamenti/{pagamento_id}", response_model=PagamentoRead)
def get_pagamento(pagamento_id: int, db: Session = Depends(get_db)):
    pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    return pagamento

@router.post("/pagamenti/", response_model=PagamentoRead)
def crea_pagamento(pagamento: PagamentoCreate, db: Session = Depends(get_db)):
    db_pagamento = Pagamento(**pagamento.model_dump())
    db.add(db_pagamento)
    db.commit()
    db.refresh(db_pagamento)
    return db_pagamento

@router.put("/pagamenti/{pagamento_id}/registra-incasso", response_model=PagamentoRead)
def registra_incasso(pagamento_id: int, metodo: MetodoPagamentoEnum, db: Session = Depends(get_db)):
    db_pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not db_pagamento:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    db_pagamento.pagato = True
    db_pagamento.data_pagamento = date.today()
    db_pagamento.metodo = metodo
    db.commit()
    db.refresh(db_pagamento)
    return db_pagamento

@router.delete("/pagamenti/{pagamento_id}")
def elimina_pagamento(pagamento_id: int, db: Session = Depends(get_db)):
    db_pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not db_pagamento:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    db.delete(db_pagamento)
    db.commit()
    return {"messaggio": "Pagamento eliminato"}
