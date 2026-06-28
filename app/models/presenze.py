from sqlalchemy import Column, Integer, String, Date, Time, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class TipoEventoEnum(enum.Enum):
    allenamento = "allenamento"
    partita = "partita"
    raduno = "raduno"
    altro = "altro"

class Evento(Base):
    __tablename__ = "eventi"

    id = Column(Integer, primary_key=True, index=True)
    gruppo_id = Column(Integer, ForeignKey("gruppi.id"), nullable=False)
    tipo = Column(Enum(TipoEventoEnum), nullable=False, default=TipoEventoEnum.allenamento)
    titolo = Column(String, nullable=False)
    data = Column(Date, nullable=False)
    ora_inizio = Column(Time, nullable=True)
    ora_fine = Column(Time, nullable=True)
    luogo = Column(String, nullable=True)
    note = Column(Text, nullable=True)
    ricorrente_id = Column(Integer, ForeignKey("eventi_ricorrenti.id"), nullable=True)

    gruppo = relationship("Gruppo", back_populates="eventi")
    presenze = relationship("Presenza", back_populates="evento")
    ricorrente = relationship("EventoRicorrente", back_populates="occorrenze")


class EventoRicorrente(Base):
    __tablename__ = "eventi_ricorrenti"

    id = Column(Integer, primary_key=True, index=True)
    gruppo_id = Column(Integer, ForeignKey("gruppi.id"), nullable=False)
    tipo = Column(Enum(TipoEventoEnum), nullable=False, default=TipoEventoEnum.allenamento)
    titolo = Column(String, nullable=False)
    ora_inizio = Column(Time, nullable=True)
    ora_fine = Column(Time, nullable=True)
    luogo = Column(String, nullable=True)
    giorni_settimana = Column(String, nullable=False)
    data_inizio = Column(Date, nullable=False)
    data_fine = Column(Date, nullable=False)
    attivo = Column(Boolean, default=True)

    occorrenze = relationship("Evento", back_populates="ricorrente")


class Presenza(Base):
    __tablename__ = "presenze"

    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventi.id"), nullable=False)
    tesserato_id = Column(Integer, ForeignKey("tesserati.id"), nullable=False)
    presente = Column(Boolean, nullable=False, default=False)
    note = Column(String, nullable=True)

    evento = relationship("Evento", back_populates="presenze")
    tesserato = relationship("Tesserato", back_populates="presenze")