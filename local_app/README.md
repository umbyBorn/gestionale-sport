# App locale offline — PGS Juvenilia Gestionale

Questa cartella contiene tutto il necessario per far girare il gestionale
**senza connessione internet** su un PC Windows, con sincronizzazione verso
il database online (Neon) quando la rete torna disponibile.

Pensata per **un solo amministratore alla volta** (nessuna gestione di
conflitti tra più operatori offline in contemporanea).

## Come funziona

- Il database locale è un file SQLite (creato automaticamente al primo
  avvio in `%APPDATA%\PGSJuvenilia\gestionale_locale.db`)
- Ogni modifica fatta (online o offline) viene registrata automaticamente
  in una tabella `sync_log` (vedi `app/sync/listeners.py`), senza bisogno
  di toccare i singoli endpoint
- La sincronizzazione manda le modifiche offline al server online e
  scarica quelle fatte online nel frattempo (vedi `app/routers/sync.py` e
  `local_app/sync_client.py`)
- I record creati offline hanno un id temporaneo negativo, che al momento
  della sincronizzazione viene sostituito con l'id reale assegnato dal
  database online (per evitare collisioni con record creati online nel
  frattempo, es. iscrizioni pubbliche)

## Passaggi per costruire l'eseguibile Windows

Va fatto **su Windows** (o WSL2 con accesso al filesystem Windows), perché
PyInstaller genera l'eseguibile per il sistema operativo su cui gira.

### 1. Build del frontend in modalità locale

Nel repo frontend:

```
REACT_APP_API_URL=http://127.0.0.1:8756 REACT_APP_LOCALE=true npm run build
```

Questo crea una cartella `build/` che punta al server locale (invece che a
Render) e mostra la voce di menu "Sincronizza".

Copia questa cartella dentro il repo backend:

```
cp -r build/ ../gestionale-sport/frontend_build/
```

### 2. Installa le dipendenze Python

Nel repo backend:

```
pip install -r requirements.txt -r local_app/requirements_locale.txt
```

### 3. Genera l'eseguibile

```
pyinstaller local_app/pgs_gestionale_locale.spec
```

L'eseguibile sarà in `dist/PGSJuvenilia/PGSJuvenilia.exe`. Puoi copiare
l'intera cartella `dist/PGSJuvenilia/` sul PC dell'amministratore (o creare
un installer con Inno Setup/NSIS se vuoi un vero e proprio programma di
installazione — non incluso qui, ma è lo step naturale successivo).

## Primo utilizzo

1. Doppio click sull'eseguibile: si apre una finestra con il gestionale
2. Vai su "Sincronizza" → inserisci l'URL del gestionale online e le tue
   credenziali amministratore → "Collega"
3. "Scarica dati iniziali" (una tantum, serve internet): copia tutto lo
   storico esistente nel database locale
4. Da qui in poi puoi lavorare anche senza rete: tutte le funzioni sono
   disponibili, i dati restano sul PC
5. Quando torna la rete: "Sincronizza ora" invia le modifiche fatte offline
   e scarica quelle fatte online nel frattempo

## Limiti noti (da tenere presente)

- **Un solo amministratore alla volta**: se più persone lavorano offline in
  parallelo su PC diversi, non c'è gestione dei conflitti — vince l'ultimo
  che sincronizza. Per quello serve l'architettura multi-utente (UUID +
  coda conflitti) discussa ma scartata per complessità.
- **Foto e documenti (Cloudinary) ed email (Resend) richiedono comunque
  internet**: se carichi un documento offline, in questa prima versione
  l'operazione fallirà finché non torna la rete. Andrebbe aggiunta una coda
  di upload in sospeso (cartella già predisposta in
  `local_app/percorsi.py::cartella_upload_in_sospeso`, ma la logica di
  invio differito non è ancora implementata: da fare in una prossima
  sessione se serve davvero usarla offline).
- **Evoluzione dello schema nel tempo**: il database locale viene creato
  dai modelli correnti al momento della clonazione, non dalla catena di
  migration Alembic (scritta per Postgres, in parte incompatibile con
  SQLite). Se in futuro cambia lo schema, il modo più semplice è ripetere
  la clonazione da zero sul PC locale.
- Il token di accesso viene salvato in `%APPDATA%\PGSJuvenilia\stato_sync.json`
  in chiaro: accettabile per un PC personale a uso esclusivo
  dell'amministratore, da evitare su PC condivisi.
