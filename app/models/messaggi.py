from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Messaggio(Base):
    __tablename__ = "messaggi"

    id = Column(Integer, primary_key=True, index=True)
    intestazione = Column(String, nullable=False)
    corpo = Column(Text, nullable=False)
    data_invio = Column(DateTime, default=datetime.utcnow)

    destinatari = relationship("MessaggioDestinatario", back_populates="messaggio")


class MessaggioDestinatario(Base):
    __tablename__ = "messaggi_destinatari"

    id = Column(Integer, primary_key=True, index=True)
    messaggio_id = Column(Integer, ForeignKey("messaggi.id"), nullable=False)
    tesserato_id = Column(Integer, ForeignKey("tesserati.id"), nullable=False)
    letto = Column(Boolean, default=False)
    email_inviata = Column(Boolean, default=False)

    messaggio = relationship("Messaggio", back_populates="destinatari")
    tesserato = relationship("Tesserato")
