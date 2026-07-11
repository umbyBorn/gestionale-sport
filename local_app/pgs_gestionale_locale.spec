# PyInstaller spec per l'app locale "PGS Juvenilia - Gestionale (offline)"
#
# Da eseguire su Windows (PyInstaller compila per il sistema operativo su
# cui gira, non è possibile generare un .exe da Linux/WSL2):
#
#   pyinstaller local_app/pgs_gestionale_locale.spec
#
# Il risultato sarà in dist/PGSJuvenilia/PGSJuvenilia.exe
#
# PRIMA di lanciare pyinstaller:
#   1. Costruire il frontend in modalità locale (vedi README.md) e copiare
#      la cartella "build" del frontend dentro backend/frontend_build/
#   2. pip install -r requirements.txt -r local_app/requirements_locale.txt

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['local_app/avvia_locale.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('alembic.ini', '.'),
        ('alembic', 'alembic'),
        ('frontend_build', 'frontend_build'),
    ],
    hiddenimports=[
        'app.models', 'app.sync.listeners', 'app.sync.core',
        'app.routers.tesserati', 'app.routers.gruppi', 'app.routers.pagamenti',
        'app.routers.staff', 'app.routers.presenze', 'app.routers.assemblee',
        'app.routers.auth', 'app.routers.calendario', 'app.routers.importazione',
        'app.routers.messaggi', 'app.routers.admin', 'app.routers.push',
        'app.routers.iscrizioni', 'app.routers.ricevute', 'app.routers.prima_nota',
        'app.routers.sync', 'local_app.router_locale',
        'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
        'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
        'uvicorn.lifespan', 'uvicorn.lifespan.on',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PGSJuvenilia',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # niente terminale visibile
    icon=None,      # eventualmente: 'local_app/icona.ico'
)
