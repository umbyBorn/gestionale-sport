from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.utenti import PushSubscription
from pydantic import BaseModel
from typing import Optional
import os
import json

router = APIRouter(prefix="/push", tags=["Push Notifications"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SubscriptionData(BaseModel):
    endpoint: str
    p256dh: str
    auth: str
    utente_id: Optional[int] = None
    tesserato_id: Optional[int] = None


@router.post("/subscribe")
def subscribe(data: SubscriptionData, db: Session = Depends(get_db)):
    existing = db.query(PushSubscription).filter(
        PushSubscription.endpoint == data.endpoint
    ).first()
    if existing:
        existing.p256dh = data.p256dh
        existing.auth = data.auth
        existing.utente_id = data.utente_id
        existing.tesserato_id = data.tesserato_id
    else:
        sub = PushSubscription(
            endpoint=data.endpoint,
            p256dh=data.p256dh,
            auth=data.auth,
            utente_id=data.utente_id,
            tesserato_id=data.tesserato_id
        )
        db.add(sub)
    db.commit()
    return {"ok": True}


@router.delete("/unsubscribe")
def unsubscribe(endpoint: str, db: Session = Depends(get_db)):
    db.query(PushSubscription).filter(
        PushSubscription.endpoint == endpoint
    ).delete()
    db.commit()
    return {"ok": True}


@router.get("/vapid-public-key")
def get_vapid_public_key():
    return {"public_key": os.getenv("VAPID_PUBLIC_KEY", "")}


def invia_push(endpoint: str, p256dh: str, auth: str, titolo: str, corpo: str) -> bool:
    try:
        from pywebpush import webpush, WebPushException
        private_key = os.getenv("VAPID_PRIVATE_KEY", "").replace("\\n", "\n")
        mailto = os.getenv("VAPID_MAILTO", "mailto:admin@example.com")
        
        webpush(
            subscription_info={
                "endpoint": endpoint,
                "keys": {"p256dh": p256dh, "auth": auth}
            },
            data=json.dumps({"title": titolo, "body": corpo}),
            vapid_private_key=private_key,
            vapid_claims={"sub": mailto}
        )
        return True
    except Exception as e:
        print(f"Errore push: {e}")
        return False


def invia_push_a_tutti(db: Session, titolo: str, corpo: str, tesserati_ids: list = None):
    query = db.query(PushSubscription)
    if tesserati_ids:
        query = query.filter(PushSubscription.tesserato_id.in_(tesserati_ids))
    subscriptions = query.all()
    
    import threading
    def _invia():
        for sub in subscriptions:
            invia_push(sub.endpoint, sub.p256dh, sub.auth, titolo, corpo)
    
    thread = threading.Thread(target=_invia, daemon=True)
    thread.start()
    return len(subscriptions)
