from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Enum, Text
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


class Genitore(Base):
    __tablename__ = "genitori"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cognome = Column(String, nullable=False)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    documento_tipo = Column(String, nullable=True)
    documento_numero = Column(String, nullable=True)
    figli = relationship("Tesserato", back_populates="genitore")


class Tesserato(Base):
    __tablename__ = "tesserati"
    id = Column(Integer, primary_key=True, index=True)
    utente_id = Column(Integer, ForeignKey("utenti.id"), nullable=True)
    genitore_id = Column(Integer, ForeignKey("genitori.id"), nullable=True)

    # Dati anagrafici base
    nome = Column(String, nullable=False)
    cognome = Column(String, nullable=False)
    data_nascita = Column(Date, nullable=False)
    codice_fiscale = Column(String(16), unique=True, nullable=False)
    sesso = Column(String(1), nullable=True)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    cellulare = Column(String, nullable=True)

    # Dati nascita
    comune_nascita = Column(String, nullable=True)
    provincia_nascita = Column(String, nullable=True)
    stato_nascita = Column(String, nullable=True)

    # Residenza
    indirizzo = Column(String, nullable=True)
    comune_residenza = Column(String, nullable=True)
    provincia_residenza = Column(String, nullable=True)
    regione_residenza = Column(String, nullable=True)
    cap_residenza = Column(String, nullable=True)

    # Dati tessera federale
    cod_tessera = Column(String, nullable=True)
    tipo_tessera = Column(String, nullable=True)
    categoria = Column(String, nullable=True)
    qualifica = Column(String, nullable=True)
    sport = Column(String, nullable=True)
    data_emissione_tessera = Column(Date, nullable=True)
    data_scadenza_tessera = Column(Date, nullable=True)
    matricola = Column(String, nullable=True)

    # Info aggiuntive
    disabile = Column(Boolean, default=False)
    straniero = Column(Boolean, default=False)
    titolo_studio = Column(String, nullable=True)
    e_socio = Column(Boolean, default=True)
    attivo = Column(Boolean, default=True)

    # Media
    foto_url = Column(String, nullable=True)

    # Relazioni
    utente = relationship("Utente", back_populates="tesserato")
    genitore = relationship("Genitore", back_populates="figli")
    gruppi = relationship("GruppoTesserato", back_populates="tesserato")
    pagamenti = relationship("Pagamento", back_populates="tesserato")
    presenze = relationship("Presenza", back_populates="tesserato")
    documenti = relationship("Documento", back_populates="tesserato")


class Documento(Base):
    __tablename__ = "documenti"
    id = Column(Integer, primary_key=True, index=True)
    tesserato_id = Column(Integer, ForeignKey("tesserati.id"), nullable=False)
    tipo = Column(String, nullable=False)
    nome_file = Column(String, nullable=False)
    url = Column(String, nullable=False)
    data_scadenza = Column(Date, nullable=True)
    note = Column(Text, nullable=True)
    tesserato = relationship("Tesserato", back_populates="documenti")


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
