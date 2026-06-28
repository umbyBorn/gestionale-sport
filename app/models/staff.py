from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class TipoRapportoEnum(enum.Enum):
    volontario = "volontario"
    cococo = "cococo"
    altro = "altro"

class TipoContrattoEnum(enum.Enum):
    sportivo = "sportivo"
    amministrativo = "amministrativo"

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cognome = Column(String, nullable=False)
    data_nascita = Column(Date, nullable=False)
    codice_fiscale = Column(String(16), unique=True, nullable=False)
    telefono = Column(String, nullable=True)
    email = Column(String, nullable=True)
    ruolo = Column(String, nullable=False)
    tipo_rapporto = Column(Enum(TipoRapportoEnum), nullable=False)
    data_inizio = Column(Date, nullable=False)
    data_fine = Column(Date, nullable=True)
    attivo = Column(Boolean, default=True)

    contratti = relationship("Contratto", back_populates="staff")
    compensi = relationship("Compenso", back_populates="staff")
    gruppi = relationship("StaffGruppo", back_populates="staff")


class StaffGruppo(Base):
    __tablename__ = "staff_gruppo"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    gruppo_id = Column(Integer, ForeignKey("gruppi.id"), nullable=False)

    staff = relationship("Staff", back_populates="gruppi")
    gruppo = relationship("Gruppo", back_populates="staff")


class Contratto(Base):
    __tablename__ = "contratti"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    tipo = Column(Enum(TipoContrattoEnum), nullable=False)
    data_inizio = Column(Date, nullable=False)
    data_fine = Column(Date, nullable=True)
    importo = Column(Numeric(10, 2), nullable=False)
    path_pdf = Column(String, nullable=True)
    firmato = Column(Boolean, default=False)

    staff = relationship("Staff", back_populates="contratti")


class Compenso(Base):
    __tablename__ = "compensi"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    importo = Column(Numeric(10, 2), nullable=False)
    data_erogazione = Column(Date, nullable=False)
    descrizione = Column(String, nullable=True)
    path_autocertificazione = Column(String, nullable=True)
    totale_progressivo = Column(Numeric(10, 2), nullable=False, default=0)
    soglia_superata = Column(Boolean, default=False)

    staff = relationship("Staff", back_populates="compensi")
