from app.models.utenti import Utente, Tesserato, Genitore, Documento, Gruppo, GruppoTesserato, PermessoOperatore, PushSubscription, RichiestaIscrizione, DatiRichiesta
from app.models.contabilita import Tariffa, Pagamento, Ricevuta, MovimentoContabile
from app.models.staff import Staff, StaffGruppo, Contratto, Compenso, DocumentoSocio
from app.models.presenze import Evento, Presenza, EventoRicorrente
from app.models.assemblee import Assemblea, PuntoOrdineGiorno, PartecipazioneAssemblea
from app.models.messaggi import Messaggio, MessaggioDestinatario
from app.models.sync import SyncLog
