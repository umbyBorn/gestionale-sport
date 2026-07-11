"""App locale PGS Juvenilia - Gestionale (funzionamento offline).

Avvia lo stesso backend FastAPI usato online, ma collegato a un database
SQLite locale invece che a Neon, e apre una finestra desktop con
l'interfaccia (nessun terminale, nessun browser da aprire a mano).

NOTE IMPORTANTI per chi la impacchetta con PyInstaller (vedi README.md in
questa cartella):
- Il database locale usa lo schema CORRENTE dei modelli (Base.metadata.create_all),
  non la catena di migration Alembic: le migration sono scritte per Postgres
  (Neon) e in parte non sono compatibili con SQLite. Il database locale
  viene quindi creato "a schema pieno" al primo avvio, non evoluto passo
  passo. Se in futuro cambia lo schema, la via più semplice è ripetere la
  clonazione iniziale (vedi sync_client.clona_da_zero).
"""
import os
import sys
import threading
import time
import webbrowser

# --- 1. Configuro l'ambiente PRIMA di importare qualunque modulo app.* ---
from local_app.percorsi import percorso_db_locale, cartella_dati

os.environ["APP_MODE"] = "locale"
os.environ.setdefault("DATABASE_URL", f"sqlite:///{percorso_db_locale()}")
os.environ.setdefault("SECRET_KEY", "chiave-locale-solo-per-uso-offline-su-questo-pc")

PORTA_LOCALE = 8756


def _percorso_risorsa(relativo: str) -> str:
    """Risolve un percorso sia in sviluppo sia dentro l'eseguibile PyInstaller
    (che estrae i file in una cartella temporanea indicata da sys._MEIPASS)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, relativo)


def _prepara_database():
    from app.database import engine, Base
    import app.models  # noqa: F401  (registra tutte le tabelle sui metadata)
    import app.sync.listeners  # noqa: F401
    Base.metadata.create_all(bind=engine)


def _avvia_server():
    import uvicorn
    from app.main import app as fastapi_app
    from fastapi.staticfiles import StaticFiles
    from local_app.router_locale import router as router_locale

    fastapi_app.include_router(router_locale)

    cartella_build = _percorso_risorsa(os.path.join("frontend_build"))
    if os.path.isdir(cartella_build):
        fastapi_app.mount("/", StaticFiles(directory=cartella_build, html=True), name="frontend")

    uvicorn.run(fastapi_app, host="127.0.0.1", port=PORTA_LOCALE, log_level="warning")


def main():
    _prepara_database()

    server_thread = threading.Thread(target=_avvia_server, daemon=True)
    server_thread.start()
    time.sleep(1.5)  # attendo che il server sia pronto

    url = f"http://127.0.0.1:{PORTA_LOCALE}/"

    try:
        import webview
        finestra = webview.create_window(
            "PGS Juvenilia - Gestionale (modalità locale)", url, width=1280, height=800
        )
        webview.start()
    except ImportError:
        # pywebview non installato: fallback, apro il browser predefinito
        webbrowser.open(url)
        print(f"App locale avviata su {url} (premi CTRL+C per chiudere)")
        while True:
            time.sleep(3600)


if __name__ == "__main__":
    main()
