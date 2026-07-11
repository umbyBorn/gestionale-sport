from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class VoceSyncLog(BaseModel):
    tabella: str
    record_id: int
    operazione: str  # insert | update | delete
    payload: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class PushRequest(BaseModel):
    voci: List[VoceSyncLog]


class MappaId(BaseModel):
    tabella: str
    id_locale: int
    id_reale: int


class PushResponse(BaseModel):
    applicate: int
    errori: List[str] = []
    mappa_id: List[MappaId] = []


class VoceSyncLogRead(VoceSyncLog):
    id: int

    class Config:
        from_attributes = True


class PullResponse(BaseModel):
    voci: List[VoceSyncLogRead]
    timestamp_server: datetime
