from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tesserati, gruppi, pagamenti, staff, presenze, assemblee
from app.routers import auth

app = FastAPI(
    title="Gestionale Sportivo",
    description="API per la gestione di associazioni sportive",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tesserati.router)
app.include_router(gruppi.router)
app.include_router(pagamenti.router)
app.include_router(staff.router)
app.include_router(presenze.router)
app.include_router(assemblee.router)

@app.get("/")
def root():
    return {"messaggio": "Gestionale Sportivo API attiva"}
