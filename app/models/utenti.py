from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class RuoloEnum(enum.Enum):
    amministratore = "amministratore"
    operatore = "operatore"
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

    # Certificato medico sportivo
    data_scadenza_certificato_medico = Column(Date, nullable=True)

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


class DocumentoSocietario(Base):
    """Documenti a livello di associazione (non legati a un singolo tesserato):
    atto costitutivo, attribuzione codice fiscale, statuto, verbali, ecc."""
    __tablename__ = "documenti_societari"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    categoria = Column(String, nullable=True)
    nome_file = Column(String, nullable=False)
    url = Column(String, nullable=False)
    data_caricamento = Column(Date, nullable=False)
    note = Column(Text, nullable=True)


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


class PermessoOperatore(Base):
    __tablename__ = "permessi_operatore"
    id = Column(Integer, primary_key=True, index=True)
    utente_id = Column(Integer, ForeignKey("utenti.id"), nullable=False)
    sezione = Column(String, nullable=False)
    abilitato = Column(Boolean, default=True)
    utente = relationship("Utente", foreign_keys=[utente_id])


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    utente_id = Column(Integer, ForeignKey("utenti.id"), nullable=True)
    tesserato_id = Column(Integer, ForeignKey("tesserati.id"), nullable=True)
    endpoint = Column(String, nullable=False, unique=True)
    p256dh = Column(String, nullable=False)
    auth = Column(String, nullable=False)


class RichiestaIscrizione(Base):
    __tablename__ = "richieste_iscrizione"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    nome_modulo = Column(String, nullable=False)
    attivo = Column(Boolean, default=True)
    created_at = Column(String, nullable=True)

    # Dati compilati dal tesserato
    richieste = relationship("DatiRichiesta", back_populates="modulo")


class DatiRichiesta(Base):
    __tablename__ = "dati_richiesta"
    id = Column(Integer, primary_key=True, index=True)
    modulo_id = Column(Integer, ForeignKey("richieste_iscrizione.id"), nullable=False)
    stato = Column(String, default="in_attesa")  # in_attesa, approvata, rifiutata
    nome = Column(String, nullable=False)
    cognome = Column(String, nullable=False)
    data_nascita = Column(String, nullable=False)
    codice_fiscale = Column(String, nullable=True)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    cellulare = Column(String, nullable=True)
    indirizzo = Column(String, nullable=True)
    comune_residenza = Column(String, nullable=True)
    provincia_residenza = Column(String, nullable=True)
    cap_residenza = Column(String, nullable=True)
    comune_nascita = Column(String, nullable=True)
    provincia_nascita = Column(String, nullable=True)
    stato_nascita = Column(String, nullable=True)
    sesso = Column(String, nullable=True)
    sport = Column(String, nullable=True)
    # Genitore (per minorenni)
    genitore_nome = Column(String, nullable=True)
    genitore_cognome = Column(String, nullable=True)
    genitore_email = Column(String, nullable=True)
    genitore_telefono = Column(String, nullable=True)
    genitore_documento_tipo = Column(String, nullable=True)
    genitore_documento_numero = Column(String, nullable=True)
    # Privacy
    consenso_privacy = Column(Boolean, default=False)
    data_invio = Column(String, nullable=True)
    note = Column(String, nullable=True)

    modulo = relationship("RichiestaIscrizione", back_populates="richieste")
