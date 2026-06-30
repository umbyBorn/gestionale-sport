from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tesserati, gruppi, pagamenti, staff, presenze, assemblee
from app.routers import auth, calendario, importazione, messaggi
from alembic.config import Config
from alembic import command
import os

app = FastAPI(
    title="Gestionale Sportivo",
    description="API per la gestione di associazioni sportive",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def esegui_migrazioni():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

app.include_router(auth.router)
app.include_router(tesserati.router)
app.include_router(gruppi.router)
app.include_router(pagamenti.router)
app.include_router(staff.router)
app.include_router(presenze.router)
app.include_router(assemblee.router)
app.include_router(calendario.router)
app.include_router(importazione.router)
app.include_router(importazione.router)
app.include_router(messaggi.router)

@app.get("/")
def root():
    return {"messaggio": "Gestionale Sportivo API attiva"}
