from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class MetodoPagamentoEnum(enum.Enum):
    contanti = "contanti"
    bonifico = "bonifico"
    altro = "altro"

class TipoMovimentoEnum(enum.Enum):
    entrata = "entrata"
    uscita = "uscita"

class Tariffa(Base):
    __tablename__ = "tariffe"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    importo = Column(Numeric(10, 2), nullable=False)
    categoria = Column(String, nullable=True)
    attiva = Column(Boolean, default=True)
    pagamenti = relationship("Pagamento", back_populates="tariffa")

class Pagamento(Base):
    __tablename__ = "pagamenti"
    id = Column(Integer, primary_key=True, index=True)
    tesserato_id = Column(Integer, ForeignKey("tesserati.id"), nullable=False)
    tariffa_id = Column(Integer, ForeignKey("tariffe.id"), nullable=False)
    importo = Column(Numeric(10, 2), nullable=False)
    data_scadenza = Column(Date, nullable=False)
    data_pagamento = Column(Date, nullable=True)
    metodo = Column(Enum(MetodoPagamentoEnum), nullable=True)
    pagato = Column(Boolean, default=False)
    contabile_allegata = Column(String, nullable=True)
    descrizione = Column(String, nullable=True)
    evento_id = Column(Integer, ForeignKey("eventi.id"), nullable=True)
    gruppo_generazione_id = Column(String, nullable=True, index=True)
    tesserato = relationship("Tesserato", back_populates="pagamenti")
    tariffa = relationship("Tariffa", back_populates="pagamenti")
    ricevuta = relationship("Ricevuta", back_populates="pagamento", uselist=False)
    evento = relationship("Evento")

class Ricevuta(Base):
    __tablename__ = "ricevute"
    id = Column(Integer, primary_key=True, index=True)
    pagamento_id = Column(Integer, ForeignKey("pagamenti.id"), nullable=False)
    numero = Column(String, unique=True, nullable=False)
    data_emissione = Column(Date, nullable=False)
    intestatario = Column(String, nullable=False)
    importo = Column(Numeric(10, 2), nullable=False)
    path_pdf = Column(String, nullable=True)
    pagamento = relationship("Pagamento", back_populates="ricevuta")

class MovimentoContabile(Base):
    __tablename__ = "movimenti_contabili"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(TipoMovimentoEnum), nullable=False)
    data = Column(Date, nullable=False)
    importo = Column(Numeric(10, 2), nullable=False)
    descrizione = Column(String, nullable=False)
    categoria = Column(String, nullable=True)
    centro_costo = Column(String, nullable=True)
    intestatario = Column(String, nullable=True)
    allegato = Column(String, nullable=True)
    note = Column(Text, nullable=True)
    pagamento_id = Column(Integer, ForeignKey("pagamenti.id"), nullable=True)

    pagamento = relationship("Pagamento")
