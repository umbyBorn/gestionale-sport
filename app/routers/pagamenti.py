import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.contabilita import Pagamento, Tariffa, MovimentoContabile
from app.models.utenti import GruppoTesserato
from app.schemas.pagamenti import (
    PagamentoCreate, PagamentoRead, PagamentoUpdate,
    TariffaCreate, TariffaRead,
    PianoScadenzeCreate, PianoScadenzeResult,
    PagamentoGruppoCreate, PagamentoGruppoResult,
)
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

router = APIRouter(tags=["Pagamenti"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _tesserati_destinatari(db: Session, tesserato_ids, gruppo_id) -> List[int]:
    """Risolve la lista di id tesserato a partire da una lista esplicita o da un gruppo."""
    if tesserato_ids:
        return list(dict.fromkeys(tesserato_ids))
    if gruppo_id:
        righe = db.query(GruppoTesserato.tesserato_id).filter(GruppoTesserato.gruppo_id == gruppo_id).all()
        return [r[0] for r in righe]
    raise HTTPException(status_code=400, detail="Specificare tesserato_ids oppure gruppo_id")


def _get_or_crea_tariffa(db: Session, nome: str, importo: float, categoria: str = None) -> Tariffa:
    tariffa = db.query(Tariffa).filter(Tariffa.nome == nome, Tariffa.attiva == True).first()
    if tariffa:
        return tariffa
    tariffa = Tariffa(nome=nome, importo=importo, categoria=categoria, attiva=True)
    db.add(tariffa)
    db.flush()
    return tariffa


# ---- PAGAMENTI: CRUD BASE ----

@router.get("/pagamenti/", response_model=List[PagamentoRead])
def lista_pagamenti(tesserato_id: int = None, db: Session = Depends(get_db)):
    q = db.query(Pagamento)
    if tesserato_id:
        q = q.filter(Pagamento.tesserato_id == tesserato_id)
    return q.order_by(Pagamento.data_scadenza.desc()).all()


@router.get("/pagamenti/scaduti/", response_model=List[PagamentoRead])
def pagamenti_scaduti(db: Session = Depends(get_db)):
    oggi = date.today()
    return db.query(Pagamento).filter(
        Pagamento.pagato == False, Pagamento.data_scadenza < oggi
    ).order_by(Pagamento.data_scadenza).all()


@router.get("/pagamenti/tesserato/{tesserato_id}", response_model=List[PagamentoRead])
def pagamenti_tesserato(tesserato_id: int, db: Session = Depends(get_db)):
    return db.query(Pagamento).filter(
        Pagamento.tesserato_id == tesserato_id
    ).order_by(Pagamento.data_scadenza).all()


@router.delete("/pagamenti/tesserato/{tesserato_id}/non-pagati")
def elimina_pagamenti_non_pagati_tesserato(tesserato_id: int, db: Session = Depends(get_db)):
    """Rimuove in blocco tutti i pagamenti non ancora pagati di un tesserato (es. creati per errore)."""
    eliminati = db.query(Pagamento).filter(
        Pagamento.tesserato_id == tesserato_id,
        Pagamento.pagato == False,
    ).delete(synchronize_session=False)
    db.commit()
    return {"eliminati": eliminati}


@router.post("/pagamenti/", response_model=PagamentoRead)
def crea_pagamento(pagamento: PagamentoCreate, db: Session = Depends(get_db)):
    db_pagamento = Pagamento(**pagamento.model_dump())
    db.add(db_pagamento)
    db.commit()
    db.refresh(db_pagamento)
    return db_pagamento


@router.put("/pagamenti/{pagamento_id}", response_model=PagamentoRead)
def aggiorna_pagamento(pagamento_id: int, dati: PagamentoUpdate, db: Session = Depends(get_db)):
    """Modifica libera di un pagamento del singolo tesserato: importo, data, tariffa, ecc."""
    db_pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not db_pagamento:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    for key, value in dati.model_dump(exclude_unset=True).items():
        setattr(db_pagamento, key, value)
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


@router.put("/pagamenti/{pagamento_id}/registra-incasso", response_model=PagamentoRead)
def registra_incasso(pagamento_id: int, metodo: str, db: Session = Depends(get_db)):
    db_pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not db_pagamento:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    db_pagamento.pagato = True
    db_pagamento.data_pagamento = date.today()
    db_pagamento.metodo = metodo
    db.commit()

    # Genera automaticamente la riga di entrata in Prima Nota, se non già presente
    esiste = db.query(MovimentoContabile).filter(MovimentoContabile.pagamento_id == pagamento_id).first()
    if not esiste:
        tariffa = db.query(Tariffa).filter(Tariffa.id == db_pagamento.tariffa_id).first()
        descrizione = db_pagamento.descrizione or (tariffa.nome if tariffa else "Incasso quota")
        movimento = MovimentoContabile(
            tipo="entrata",
            data=db_pagamento.data_pagamento,
            importo=db_pagamento.importo,
            descrizione=descrizione,
            categoria=(tariffa.categoria if tariffa else None),
            pagamento_id=db_pagamento.id,
        )
        db.add(movimento)
        db.commit()

    db.refresh(db_pagamento)
    return db_pagamento


# ---- GENERAZIONE AUTOMATICA SCADENZE (es. Iscrizione + quote da Settembre a Giugno) ----

@router.post("/pagamenti/piano-scadenze", response_model=PianoScadenzeResult)
def genera_piano_scadenze(piano: PianoScadenzeCreate, db: Session = Depends(get_db)):
    tesserato_ids = _tesserati_destinatari(db, piano.tesserato_ids, piano.gruppo_id)
    if not tesserato_ids:
        raise HTTPException(status_code=400, detail="Nessun tesserato destinatario trovato")
    if not piano.voci:
        raise HTTPException(status_code=400, detail="Specificare almeno una voce di scadenza")

    batch_id = str(uuid.uuid4())
    creati = 0
    for voce in piano.voci:
        tariffa = _get_or_crea_tariffa(db, voce.nome, voce.importo, piano.categoria_tariffa)
        for tid in tesserato_ids:
            db.add(Pagamento(
                tesserato_id=tid,
                tariffa_id=tariffa.id,
                importo=voce.importo,
                data_scadenza=voce.data_scadenza,
                pagato=False,
                descrizione=voce.nome,
                gruppo_generazione_id=batch_id,
            ))
            creati += 1
    db.commit()
    return PianoScadenzeResult(
        tesserati_coinvolti=len(tesserato_ids),
        pagamenti_creati=creati,
        gruppo_generazione_id=batch_id,
    )


# ---- PAGAMENTI AD HOC DI GRUPPO (completino, gita, torneo...) ----

@router.post("/pagamenti/gruppo", response_model=PagamentoGruppoResult)
def crea_pagamento_gruppo(dati: PagamentoGruppoCreate, db: Session = Depends(get_db)):
    tesserato_ids = _tesserati_destinatari(db, dati.tesserato_ids, dati.gruppo_id)
    if not tesserato_ids:
        raise HTTPException(status_code=400, detail="Nessun tesserato destinatario trovato")

    tariffa = _get_or_crea_tariffa(db, dati.nome, dati.importo, "Pagamenti vari")
    batch_id = str(uuid.uuid4())
    for tid in tesserato_ids:
        db.add(Pagamento(
            tesserato_id=tid,
            tariffa_id=tariffa.id,
            importo=dati.importo,
            data_scadenza=dati.data_scadenza,
            pagato=False,
            descrizione=dati.nome,
            evento_id=dati.evento_id,
            gruppo_generazione_id=batch_id,
        ))
    db.commit()
    return PagamentoGruppoResult(
        tesserati_coinvolti=len(tesserato_ids),
        pagamenti_creati=len(tesserato_ids),
        gruppo_generazione_id=batch_id,
    )


@router.get("/pagamenti/batch/{gruppo_generazione_id}", response_model=List[PagamentoRead])
def pagamenti_del_batch(gruppo_generazione_id: str, db: Session = Depends(get_db)):
    """Utile per modificare/annullare in blocco una generazione (es. tutte le rate di un piano)."""
    return db.query(Pagamento).filter(Pagamento.gruppo_generazione_id == gruppo_generazione_id).all()


class ModificaBatchInput(BaseModel):
    importo: Optional[float] = None
    data_scadenza: Optional[date] = None
    solo_non_pagati: bool = True

@router.put("/pagamenti/batch/{gruppo_generazione_id}")
def modifica_batch(gruppo_generazione_id: str, dati: ModificaBatchInput, db: Session = Depends(get_db)):
    """Applica una modifica (importo e/o data scadenza) a tutti i pagamenti di una generazione in blocco."""
    q = db.query(Pagamento).filter(Pagamento.gruppo_generazione_id == gruppo_generazione_id)
    if dati.solo_non_pagati:
        q = q.filter(Pagamento.pagato == False)
    pagamenti = q.all()
    for p in pagamenti:
        if dati.importo is not None:
            p.importo = dati.importo
        if dati.data_scadenza is not None:
            p.data_scadenza = dati.data_scadenza
    db.commit()
    return {"modificati": len(pagamenti)}


@router.delete("/pagamenti/batch/{gruppo_generazione_id}")
def elimina_batch(gruppo_generazione_id: str, solo_non_pagati: bool = True, db: Session = Depends(get_db)):
    q = db.query(Pagamento).filter(Pagamento.gruppo_generazione_id == gruppo_generazione_id)
    if solo_non_pagati:
        q = q.filter(Pagamento.pagato == False)
    eliminati = q.delete(synchronize_session=False)
    db.commit()
    return {"eliminati": eliminati}


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
