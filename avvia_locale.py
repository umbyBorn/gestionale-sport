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
    from fastapi.responses import FileResponse
    from local_app.router_locale import router as router_locale

    fastapi_app.include_router(router_locale)

    cartella_build = _percorso_risorsa(os.path.join("frontend_build"))
    if os.path.isdir(cartella_build):
        # app/main.py definisce una route esplicita GET "/" (health-check usata
        # su Render): la rimuovo solo qui, altrimenti avrebbe sempre la
        # precedenza sull'interfaccia servita in locale.
        fastapi_app.router.routes = [
            r for r in fastapi_app.router.routes
            if not (getattr(r, "path", None) == "/" and "GET" in getattr(r, "methods", set()))
        ]

        # I file JS/CSS della build (cartella build/static/) su un sotto-percorso
        # dedicato: NON monto nulla su "/", altrimenti intercetterebbe anche le
        # chiamate API (es. /auth/login) prima che arrivino ai router veri.
        cartella_static_build = os.path.join(cartella_build, "static")
        if os.path.isdir(cartella_static_build):
            fastapi_app.mount("/static", StaticFiles(directory=cartella_static_build), name="static_build")

        percorso_index = os.path.join(cartella_build, "index.html")

        # Route "raccogli-tutto", registrata per ULTIMA (dopo tutti gli
        # include_router già fatti in app/main.py): Starlette controlla prima
        # le route specifiche (API), quindi questa scatta solo se nessuna
        # route API corrisponde. Serve i file reali della build (favicon,
        # manifest.json...) se esistono, altrimenti index.html — così anche
        # il routing lato client di React funziona su un refresh diretto.
        @fastapi_app.get("/{percorso_completo:path}", include_in_schema=False)
        def servi_frontend(percorso_completo: str):
            candidato = os.path.join(cartella_build, percorso_completo)
            if percorso_completo and os.path.isfile(candidato):
                return FileResponse(candidato)
            return FileResponse(percorso_index)
    else:
        print(f"ATTENZIONE: cartella frontend non trovata in {cartella_build}, servo solo l'API")

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
        webview.start(debug=True)
    except ImportError:
        # pywebview non installato: fallback, apro il browser predefinito
        webbrowser.open(url)
        print(f"App locale avviata su {url} (premi CTRL+C per chiudere)")
        while True:
            time.sleep(3600)


if __name__ == "__main__":
    main()
