from sqlalchemy import Column, Integer, String, Date, Time, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class StatoAssembleaEnum(enum.Enum):
    pianificata = "pianificata"
    conclusa = "conclusa"
    annullata = "annullata"

class TipoVotoEnum(enum.Enum):
    favorevole = "favorevole"
    contrario = "contrario"
    astenuto = "astenuto"

class Assemblea(Base):
    __tablename__ = "assemblee"

    id = Column(Integer, primary_key=True, index=True)
    titolo = Column(String, nullable=False)
    data = Column(Date, nullable=False)
    ora = Column(Time, nullable=True)
    luogo = Column(String, nullable=True)
    stato = Column(Enum(StatoAssembleaEnum), nullable=False, default=StatoAssembleaEnum.pianificata)
    path_verbale = Column(String, nullable=True)
    note = Column(Text, nullable=True)

    punti_ordine_giorno = relationship("PuntoOrdineGiorno", back_populates="assemblea")
    partecipanti = relationship("PartecipazioneAssemblea", back_populates="assemblea")


class PuntoOrdineGiorno(Base):
    __tablename__ = "punti_ordine_giorno"

    id = Column(Integer, primary_key=True, index=True)
    assemblea_id = Column(Integer, ForeignKey("assemblee.id"), nullable=False)
    numero = Column(Integer, nullable=False)
    titolo = Column(String, nullable=False)
    descrizione = Column(Text, nullable=True)
    esito = Column(Text, nullable=True)

    assemblea = relationship("Assemblea", back_populates="punti_ordine_giorno")


class PartecipazioneAssemblea(Base):
    __tablename__ = "partecipazioni_assemblea"

    id = Column(Integer, primary_key=True, index=True)
    assemblea_id = Column(Integer, ForeignKey("assemblee.id"), nullable=False)
    tesserato_id = Column(Integer, ForeignKey("tesserati.id"), nullable=False)
    presente = Column(Boolean, default=False)
    delega_a_id = Column(Integer, ForeignKey("tesserati.id"), nullable=True)
    voto = Column(Enum(TipoVotoEnum), nullable=True)

    assemblea = relationship("Assemblea", back_populates="partecipanti")
    tesserato = relationship("Tesserato", foreign_keys=[tesserato_id])
    delegato_a = relationship("Tesserato", foreign_keys=[delega_a_id])
