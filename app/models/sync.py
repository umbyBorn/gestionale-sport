from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class SyncLog(Base):
    """Registro di tutte le modifiche (creazione/modifica/cancellazione) fatte
    su una qualsiasi tabella dell'applicazione. Popolato automaticamente da
    app/sync/listeners.py tramite eventi SQLAlchemy, senza bisogno di
    modificare i singoli endpoint.

    Usato per il funzionamento offline: la stessa applicazione, quando gira
    in locale su un database SQLite, scrive qui ogni modifica; al momento
    della sincronizzazione queste righe vengono confrontate/inviate al
    database online (Neon) e viceversa.
    """
    __tablename__ = "sync_log"

    id = Column(Integer, primary_key=True, index=True)
    tabella = Column(String, nullable=False, index=True)
    record_id = Column(Integer, nullable=False, index=True)
    operazione = Column(String, nullable=False)  # insert | update | delete
    payload = Column(Text, nullable=True)  # JSON della riga (insert/update); vuoto per delete
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    sincronizzato = Column(Boolean, default=False, nullable=False, index=True)
    origine = Column(String, nullable=False, default="locale")  # 'locale' oppure 'online'
