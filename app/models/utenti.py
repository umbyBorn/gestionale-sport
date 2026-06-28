from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class RuoloEnum(enum.Enum):
    amministratore = "amministratore"
    staff = "staff"
    commercialista = "commercialista"
    tesserato = "tesserato"
    genitore = "genitore"

class Utente(Base):
    __tablename__ = "utenti"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    ruolo = Column(Enum(RuoloEnum), nullable=False)
    attivo = Column(Boolean, default=True)
    tesserato = relationship("Tesserato", back_populates="utente", uselist=False)

class Tesserato(Base):
    __tablename__ = "tesserati"
    id = Column(Integer, primary_key=True, index=True)
    utente_id = Column(Integer, ForeignKey("utenti.id"), nullable=True)
    nome = Column(String, nullable=False)
    cognome = Column(String, nullable=False)
    data_nascita = Column(Date, nullable=False)
    codice_fiscale = Column(String(16), unique=True, nullable=False)
    telefono = Column(String, nullable=True)
    indirizzo = Column(String, nullable=True)
    e_socio = Column(Boolean, default=True)
    attivo = Column(Boolean, default=True)
    utente = relationship("Utente", back_populates="tesserato")
    genitore_id = Column(Integer, ForeignKey("tesserati.id"), nullable=True)
    genitore = relationship("Tesserato", remote_side=[id], foreign_keys=[genitore_id])
    gruppi = relationship("GruppoTesserato", back_populates="tesserato")
    pagamenti = relationship("Pagamento", back_populates="tesserato")
    presenze = relationship("Presenza", back_populates="tesserato")

class Gruppo(Base):
    __tablename__ = "gruppi"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descrizione = Column(String, nullable=True)
    attivo = Column(Boolean, default=True)
    tesserati = relationship("GruppoTesserato", back_populates="gruppo")
    eventi = relationship("Evento", back_populates="gruppo")
    staff = relationship("StaffGruppo", back_populates="gruppo")

class GruppoTesserato(Base):
    __tablename__ = "gruppo_tesserato"
    id = Column(Integer, primary_key=True, index=True)
    gruppo_id = Column(Integer, ForeignKey("gruppi.id"), nullable=False)
    tesserato_id = Column(Integer, ForeignKey("tesserati.id"), nullable=False)
    data_iscrizione = Column(Date, nullable=False)
    gruppo = relationship("Gruppo", back_populates="tesserati")
    tesserato = relationship("Tesserato", back_populates="gruppi")
