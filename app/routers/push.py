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
    p256dh: Optional[str] = None
    auth: Optional[str] = None
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
@router.post("/test-send/{subscription_id}")
def test_send(subscription_id: int, db: Session = Depends(get_db)):
    sub = db.query(PushSubscription).filter(PushSubscription.id == subscription_id).first()
    if not sub:
        return {"error": "subscription non trovata"}
    try:
        from pywebpush import webpush
        import json
        import base64
        from cryptography.hazmat.primitives.serialization import load_der_private_key
        private_key_b64 = os.getenv("VAPID_PRIVATE_KEY", "")
        if private_key_b64.startswith("-----"):
            private_key = private_key_b64.replace("\\n", "\n")
        else:
            padding = '=' * (4 - len(private_key_b64) % 4) if len(private_key_b64) % 4 else ''
            private_key_der = base64.urlsafe_b64decode(private_key_b64 + padding)
            private_key_obj = load_der_private_key(private_key_der, password=None)
            from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
            private_key = private_key_obj.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode()
        mailto = os.getenv("VAPID_MAILTO", "mailto:admin@example.com")
        webpush(
            subscription_info={"endpoint": sub.endpoint, "keys": {"p256dh": sub.p256dh, "auth": sub.auth}},
            data=json.dumps({"title": "Test PGS Juvenilia", "body": "Test push"}),
            vapid_private_key=private_key,
            vapid_claims={"sub": mailto}
        )
        return {"ok": True, "endpoint": sub.endpoint[:50]}
    except Exception as e:
        return {"ok": False, "errore": str(e), "endpoint": sub.endpoint[:50]}

@router.delete("/clear-all")
def clear_all_subscriptions(db: Session = Depends(get_db)):
    n = db.query(PushSubscription).delete()
    db.commit()
    return {"eliminati": n}

@router.get("/subscriptions")
def lista_subscriptions(db: Session = Depends(get_db)):
    subs = db.query(PushSubscription).all()
    return [{"id": s.id, "endpoint": s.endpoint[:50]+"...", "tesserato_id": s.tesserato_id, "utente_id": s.utente_id} for s in subs]


@router.get("/vapid-public-key")
def get_vapid_public_key():
    return {"public_key": os.getenv("VAPID_PUBLIC_KEY", "")}


def invia_push(endpoint: str, p256dh: str, auth: str, titolo: str, corpo: str) -> bool:
    try:
        from pywebpush import webpush, WebPushException
        private_key = os.getenv("VAPID_PRIVATE_KEY", "").replace("\\n", "\n")
        mailto = os.getenv("VAPID_MAILTO", "mailto:admin@example.com")
        
        print(f"[PUSH] Invio a endpoint: {endpoint[:50]}...")
        print(f"[PUSH] Chiave privata presente: {bool(private_key)}, lunghezza: {len(private_key)}")
        print(f"[PUSH] Contiene BEGIN: {'BEGIN PRIVATE KEY' in private_key}")
        
        webpush(
            subscription_info={
                "endpoint": endpoint,
                "keys": {"p256dh": p256dh, "auth": auth}
            },
            data=json.dumps({"title": titolo, "body": corpo}),
            vapid_private_key=private_key,
            vapid_claims={"sub": mailto}
        )
        print(f"[PUSH] Inviata con successo a {endpoint[:50]}")
        return True
    except Exception as e:
        print(f"[PUSH] Errore: {type(e).__name__}: {e}")
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
