import React, { useEffect, useState } from 'react';
import {
  getTesserati, creaTesserato, aggiornaTesserato, eliminaTesserato,
  getGruppi, getGruppiTesserato, aggiornaGruppiTesserato
} from '../services/api';
import axios from 'axios';

const API_URL = 'https://gestionale-sport-api.onrender.com';

// ---- Tipi ----
interface Genitore {
  id: number;
  nome: string;
  cognome: string;
  email?: string;
  telefono?: string;
  documento_tipo?: string;
  documento_numero?: string;
}

interface Documento {
  id: number;
  tipo: string;
  nome_file: string;
  url: string;
  data_scadenza?: string;
  note?: string;
}

interface Tesserato {
  id: number;
  nome: string;
  cognome: string;
  data_nascita: string;
  codice_fiscale: string;
  sesso?: string;
  email?: string;
  telefono?: string;
  cellulare?: string;
  comune_nascita?: string;
  provincia_nascita?: string;
  stato_nascita?: string;
  indirizzo?: string;
  comune_residenza?: string;
  provincia_residenza?: string;
  regione_residenza?: string;
  cap_residenza?: string;
  cod_tessera?: string;
  tipo_tessera?: string;
  categoria?: string;
  qualifica?: string;
  sport?: string;
  data_emissione_tessera?: string;
  data_scadenza_tessera?: string;
  matricola?: string;
  disabile: boolean;
  straniero: boolean;
  titolo_studio?: string;
  e_socio: boolean;
  genitore_id?: number;
  foto_url?: string;
  attivo: boolean;
  genitore?: Genitore;
  documenti?: Documento[];
}

interface Gruppo { id: number; nome: string; }

const formVuoto: Omit<Tesserato, 'id' | 'attivo' | 'genitore' | 'documenti'> = {
  nome: '', cognome: '', data_nascita: '', codice_fiscale: '',
  sesso: '', email: '', telefono: '', cellulare: '',
  comune_nascita: '', provincia_nascita: '', stato_nascita: '',
  indirizzo: '', comune_residenza: '', provincia_residenza: '',
  regione_residenza: '', cap_residenza: '',
  cod_tessera: '', tipo_tessera: '', categoria: '', qualifica: '',
  sport: '', data_emissione_tessera: '', data_scadenza_tessera: '',
  matricola: '', disabile: false, straniero: false,
  titolo_studio: '', e_socio: true, genitore_id: undefined, foto_url: '',
};

type Tab = 'anagrafica' | 'residenza' | 'tessera' | 'genitore' | 'documenti';

// ---- Campo helper ----
const Campo: React.FC<{
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  colSpan?: number;
}> = ({ label, value, onChange, type = 'text', colSpan = 1 }) => (
  <div className={colSpan === 2 ? 'col-span-2' : ''}>
    <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
    <input
      type={type}
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  </div>
);

// ---- Componente principale ----
const Tesserati: React.FC = () => {
  const [tesserati, setTesserati] = useState<Tesserato[]>([]);
  const [gruppi, setGruppi] = useState<Gruppo[]>([]);
  const [loading, setLoading] = useState(true);
  const [mostraForm, setMostraForm] = useState(false);
  const [mostraDettaglio, setMostraDettaglio] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [dettaglio, setDettaglio] = useState<Tesserato | null>(null);
  const [documentiDettaglio, setDocumentiDettaglio] = useState<Documento[]>([]);
  const [ricerca, setRicerca] = useState('');
  const [form, setForm] = useState<typeof formVuoto>({ ...formVuoto });
  const [gruppiSelezionati, setGruppiSelezionati] = useState<number[]>([]);
  const [tab, setTab] = useState<Tab>('anagrafica');
  const [mostraDisattivati, setMostraDisattivati] = useState(false);
  const [fileDocumento, setFileDocumento] = useState<File | null>(null);
  const [tipoDocumento, setTipoDocumento] = useState('');
  const [scadenzaDocumento, setScadenzaDocumento] = useState('');
  const [caricandoDoc, setCaricandoDoc] = useState(false);
  const [fotoFile, setFotoFile] = useState<File | null>(null);

  const caricaTesserati = () => {
    const endpoint = mostraDisattivati ? '/tesserati/tutti' : '/tesserati/';
    const token = localStorage.getItem('token');
    axios.get(`${API_URL}${endpoint}`, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => { setTesserati(res.data); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { caricaTesserati(); }, [mostraDisattivati]);
  useEffect(() => { getGruppi().then(res => setGruppi(res.data)); }, []);

  const apriNuovo = () => {
    setEditingId(null);
    setForm({ ...formVuoto });
    setGruppiSelezionati([]);
    setTab('anagrafica');
    setMostraForm(true);
  };

  const apriModifica = async (t: Tesserato) => {
    setEditingId(t.id);
    setForm({
      nome: t.nome, cognome: t.cognome, data_nascita: t.data_nascita,
      codice_fiscale: t.codice_fiscale, sesso: t.sesso || '',
      email: t.email || '', telefono: t.telefono || '', cellulare: t.cellulare || '',
      comune_nascita: t.comune_nascita || '', provincia_nascita: t.provincia_nascita || '',
      stato_nascita: t.stato_nascita || '', indirizzo: t.indirizzo || '',
      comune_residenza: t.comune_residenza || '', provincia_residenza: t.provincia_residenza || '',
      regione_residenza: t.regione_residenza || '', cap_residenza: t.cap_residenza || '',
      cod_tessera: t.cod_tessera || '', tipo_tessera: t.tipo_tessera || '',
      categoria: t.categoria || '', qualifica: t.qualifica || '',
      sport: t.sport || '', data_emissione_tessera: t.data_emissione_tessera || '',
      data_scadenza_tessera: t.data_scadenza_tessera || '', matricola: t.matricola || '',
      disabile: t.disabile, straniero: t.straniero, titolo_studio: t.titolo_studio || '',
      e_socio: t.e_socio, genitore_id: t.genitore_id, foto_url: t.foto_url || '',
    });
    const res = await getGruppiTesserato(t.id);
    setGruppiSelezionati(res.data);
    setTab('anagrafica');
    setMostraForm(true);
  };

  const apriDettaglio = async (t: Tesserato) => {
    const token = localStorage.getItem('token');
    const res = await axios.get(`${API_URL}/tesserati/${t.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setDettaglio(res.data);
    setDocumentiDettaglio(res.data.documenti || []);
    setMostraDettaglio(true);
  };

  const toggleGruppo = (id: number) => {
    setGruppiSelezionati(prev => prev.includes(id) ? prev.filter(g => g !== id) : [...prev, id]);
  };

  const setF = (key: string, value: any) => setForm(prev => ({ ...prev, [key]: value }));

  const handleSubmit = async () => {
    if (!form.codice_fiscale.trim()) {
      if (!window.confirm('Codice Fiscale non inserito. Continuare comunque?')) return;
    }
    const payload = { ...form };
    // Converti stringhe vuote in null per i campi data
    ['data_emissione_tessera', 'data_scadenza_tessera'].forEach(k => {
      if (!(payload as any)[k]) (payload as any)[k] = null;
    });
    let id = editingId;
    if (editingId) {
      await aggiornaTesserato(editingId, payload);
    } else {
      const res = await creaTesserato(payload);
      id = res.data.id;
    }
    if (id) await aggiornaGruppiTesserato(id, gruppiSelezionati);

    // Upload foto se selezionata
    if (fotoFile && id) {
      const fd = new FormData();
      fd.append('file', fotoFile);
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/tesserati/${id}/foto`, fd, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' }
      });
    }

    setMostraForm(false);
    setEditingId(null);
    setForm({ ...formVuoto });
    setGruppiSelezionati([]);
    setFotoFile(null);
    caricaTesserati();
  };

  const handleElimina = async (id: number) => {
    if (window.confirm('Vuoi disattivare questo tesserato?')) {
      await eliminaTesserato(id);
      caricaTesserati();
    }
  };

  const handleRiattiva = async (id: number) => {
    const token = localStorage.getItem('token');
    await axios.put(`${API_URL}/tesserati/${id}/riattiva`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    caricaTesserati();
  };

  const handleCaricaDocumento = async () => {
    if (!fileDocumento || !tipoDocumento || !dettaglio) return;
    setCaricandoDoc(true);
    const fd = new FormData();
    fd.append('file', fileDocumento);
    fd.append('tipo', tipoDocumento);
    if (scadenzaDocumento) fd.append('data_scadenza', scadenzaDocumento);
    const token = localStorage.getItem('token');
    const res = await axios.post(`${API_URL}/tesserati/${dettaglio.id}/documenti`, fd, {
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' }
    });
    setDocumentiDettaglio(prev => [...prev, res.data]);
    setFileDocumento(null);
    setTipoDocumento('');
    setScadenzaDocumento('');
    setCaricandoDoc(false);
  };

  const handleEliminaDocumento = async (docId: number) => {
    const token = localStorage.getItem('token');
    await axios.delete(`${API_URL}/tesserati/documenti/${docId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setDocumentiDettaglio(prev => prev.filter(d => d.id !== docId));
  };

  const filtrati = tesserati.filter(t =>
    `${t.nome} ${t.cognome} ${t.codice_fiscale} ${t.categoria || ''}`.toLowerCase()
      .includes(ricerca.toLowerCase())
  );

  const TABS: { id: Tab; label: string }[] = [
    { id: 'anagrafica', label: 'Anagrafica' },
    { id: 'residenza', label: 'Residenza' },
    { id: 'tessera', label: 'Tessera' },
    { id: 'genitore', label: 'Genitore' },
    { id: 'documenti', label: 'Gruppi' },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-blue-800 text-white px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <a href="/" className="text-white hover:text-blue-200 text-sm">← Dashboard</a>
          <h1 className="text-xl font-bold">Tesserati</h1>
        </div>
        <button onClick={apriNuovo} className="bg-white text-blue-800 px-4 py-1 rounded font-medium text-sm hover:bg-blue-50">
          + Nuovo tesserato
        </button>
      </header>

      <main className="p-6">
        {/* Barra ricerca e filtri */}
        <div className="flex gap-4 items-center mb-6 flex-wrap">
          <input
            type="text"
            placeholder="Cerca per nome, cognome, CF, categoria..."
            value={ricerca}
            onChange={e => setRicerca(e.target.value)}
            className="flex-1 min-w-64 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
            <input type="checkbox" checked={mostraDisattivati} onChange={e => setMostraDisattivati(e.target.checked)} />
            Mostra disattivati
          </label>
          <span className="text-sm text-gray-400">{filtrati.length} tesserati</span>
        </div>

        {/* Tabella */}
        {loading ? (
          <p className="text-gray-500">Caricamento...</p>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-blue-800 text-white">
                <tr>
                  <th className="px-4 py-3 text-left">Nome</th>
                  <th className="px-4 py-3 text-left">Cognome</th>
                  <th className="px-4 py-3 text-left">Cod. Fiscale</th>
                  <th className="px-4 py-3 text-left">Categoria</th>
                  <th className="px-4 py-3 text-left">Tessera</th>
                  <th className="px-4 py-3 text-left">Scad. tessera</th>
                  <th className="px-4 py-3 text-left">Socio</th>
                  <th className="px-4 py-3 text-left">Stato</th>
                  <th className="px-4 py-3 text-left">Azioni</th>
                </tr>
              </thead>
              <tbody>
                {filtrati.map((t, i) => (
                  <tr key={t.id} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-4 py-3 font-medium">{t.nome}</td>
                    <td className="px-4 py-3">{t.cognome}</td>
                    <td className="px-4 py-3 font-mono text-xs">{t.codice_fiscale}</td>
                    <td className="px-4 py-3">{t.categoria || '-'}</td>
                    <td className="px-4 py-3 text-xs">{t.cod_tessera || '-'}</td>
                    <td className="px-4 py-3 text-xs">
                      {t.data_scadenza_tessera ? (
                        <span className={new Date(t.data_scadenza_tessera) < new Date() ? 'text-red-600 font-medium' : ''}>
                          {t.data_scadenza_tessera}
                        </span>
                      ) : '-'}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${t.e_socio ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                        {t.e_socio ? 'Sì' : 'No'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${t.attivo ? 'bg-blue-100 text-blue-700' : 'bg-red-100 text-red-600'}`}>
                        {t.attivo ? 'Attivo' : 'Disattivo'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-3">
                        <button onClick={() => apriDettaglio(t)} className="text-gray-500 hover:text-gray-700 text-xs">Dettaglio</button>
                        <button onClick={() => apriModifica(t)} className="text-blue-600 hover:text-blue-800 text-xs">Modifica</button>
                        {t.attivo
                          ? <button onClick={() => handleElimina(t.id)} className="text-red-500 hover:text-red-700 text-xs">Disattiva</button>
                          : <button onClick={() => handleRiattiva(t.id)} className="text-green-600 hover:text-green-800 text-xs">Riattiva</button>
                        }
                      </div>
                    </td>
                  </tr>
                ))}
                {filtrati.length === 0 && (
                  <tr><td colSpan={9} className="px-4 py-8 text-center text-gray-400">Nessun tesserato trovato</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* ---- FORM CREAZIONE/MODIFICA ---- */}
        {mostraForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
              <div className="px-6 pt-6 pb-4 border-b">
                <h2 className="text-lg font-bold text-gray-800">{editingId ? 'Modifica Tesserato' : 'Nuovo Tesserato'}</h2>
                {/* Tab bar */}
                <div className="flex gap-1 mt-4 overflow-x-auto">
                  {TABS.map(t => (
                    <button key={t.id} onClick={() => setTab(t.id)}
                      className={`px-3 py-1.5 rounded text-xs font-medium whitespace-nowrap ${tab === t.id ? 'bg-blue-700 text-white' : 'text-gray-600 hover:bg-gray-100'}`}>
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="overflow-y-auto px-6 py-4 flex-1">
                {/* TAB: Anagrafica */}
                {tab === 'anagrafica' && (
                  <div className="grid grid-cols-2 gap-4">
                    <Campo label="Nome *" value={form.nome} onChange={v => setF('nome', v)} />
                    <Campo label="Cognome *" value={form.cognome} onChange={v => setF('cognome', v)} />
                    <Campo label="Data di nascita *" value={form.data_nascita} onChange={v => setF('data_nascita', v)} type="date" />
                    <Campo label="Codice Fiscale" value={form.codice_fiscale} onChange={v => setF('codice_fiscale', v.toUpperCase())} />
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Sesso</label>
                      <select value={form.sesso || ''} onChange={e => setF('sesso', e.target.value)}
                        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">-</option>
                        <option value="M">Maschio</option>
                        <option value="F">Femmina</option>
                      </select>
                    </div>
                    <Campo label="Email" value={form.email || ''} onChange={v => setF('email', v)} type="email" />
                    <Campo label="Telefono" value={form.telefono || ''} onChange={v => setF('telefono', v)} />
                    <Campo label="Cellulare" value={form.cellulare || ''} onChange={v => setF('cellulare', v)} />
                    <Campo label="Comune di nascita" value={form.comune_nascita || ''} onChange={v => setF('comune_nascita', v)} />
                    <Campo label="Provincia nascita" value={form.provincia_nascita || ''} onChange={v => setF('provincia_nascita', v)} />
                    <Campo label="Stato di nascita" value={form.stato_nascita || ''} onChange={v => setF('stato_nascita', v)} />
                    <Campo label="Titolo di studio" value={form.titolo_studio || ''} onChange={v => setF('titolo_studio', v)} />
                    <div className="col-span-2 flex gap-6">
                      <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                        <input type="checkbox" checked={form.e_socio} onChange={e => setF('e_socio', e.target.checked)} />
                        È socio
                      </label>
                      <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                        <input type="checkbox" checked={form.disabile} onChange={e => setF('disabile', e.target.checked)} />
                        Disabile
                      </label>
                      <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                        <input type="checkbox" checked={form.straniero} onChange={e => setF('straniero', e.target.checked)} />
                        Straniero
                      </label>
                    </div>
                    <div className="col-span-2">
                      <label className="block text-xs font-medium text-gray-600 mb-1">Foto profilo</label>
                      <input type="file" accept="image/*" onChange={e => setFotoFile(e.target.files?.[0] || null)}
                        className="text-sm text-gray-600" />
                      {form.foto_url && <img src={form.foto_url} alt="foto" className="mt-2 w-16 h-16 rounded-full object-cover" />}
                    </div>
                  </div>
                )}

                {/* TAB: Residenza */}
                {tab === 'residenza' && (
                  <div className="grid grid-cols-2 gap-4">
                    <Campo label="Indirizzo" value={form.indirizzo || ''} onChange={v => setF('indirizzo', v)} colSpan={2} />
                    <Campo label="Comune di residenza" value={form.comune_residenza || ''} onChange={v => setF('comune_residenza', v)} />
                    <Campo label="CAP" value={form.cap_residenza || ''} onChange={v => setF('cap_residenza', v)} />
                    <Campo label="Provincia" value={form.provincia_residenza || ''} onChange={v => setF('provincia_residenza', v)} />
                    <Campo label="Regione" value={form.regione_residenza || ''} onChange={v => setF('regione_residenza', v)} />
                  </div>
                )}

                {/* TAB: Tessera */}
                {tab === 'tessera' && (
                  <div className="grid grid-cols-2 gap-4">
                    <Campo label="Codice tessera" value={form.cod_tessera || ''} onChange={v => setF('cod_tessera', v)} />
                    <Campo label="Tipo tessera" value={form.tipo_tessera || ''} onChange={v => setF('tipo_tessera', v)} />
                    <Campo label="Categoria" value={form.categoria || ''} onChange={v => setF('categoria', v)} />
                    <Campo label="Qualifica" value={form.qualifica || ''} onChange={v => setF('qualifica', v)} />
                    <Campo label="Sport" value={form.sport || ''} onChange={v => setF('sport', v)} />
                    <Campo label="Matricola" value={form.matricola || ''} onChange={v => setF('matricola', v)} />
                    <Campo label="Data emissione" value={form.data_emissione_tessera || ''} onChange={v => setF('data_emissione_tessera', v)} type="date" />
                    <Campo label="Data scadenza" value={form.data_scadenza_tessera || ''} onChange={v => setF('data_scadenza_tessera', v)} type="date" />
                  </div>
                )}

                {/* TAB: Genitore */}
                {tab === 'genitore' && (
                  <div>
                    <p className="text-sm text-gray-500 mb-4">Associa un genitore/tutore (per i tesserati minorenni).</p>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">ID Genitore</label>
                      <input
                        type="number"
                        value={form.genitore_id || ''}
                        onChange={e => setF('genitore_id', e.target.value ? parseInt(e.target.value) : undefined)}
                        placeholder="Inserisci l'ID del genitore"
                        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <p className="text-xs text-gray-400 mt-1">I genitori si gestiscono dalla sezione Genitori (in sviluppo).</p>
                    </div>
                  </div>
                )}

                {/* TAB: Gruppi */}
                {tab === 'documenti' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">Gruppi / Corsi</label>
                    <div className="flex flex-wrap gap-2">
                      {gruppi.map(g => (
                        <button key={g.id} type="button" onClick={() => toggleGruppo(g.id)}
                          className={`px-3 py-1.5 rounded-full text-sm border ${
                            gruppiSelezionati.includes(g.id)
                              ? 'bg-blue-700 text-white border-blue-700'
                              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                          }`}>
                          {g.nome}
                        </button>
                      ))}
                      {gruppi.length === 0 && <p className="text-xs text-gray-400">Nessun gruppo creato ancora</p>}
                    </div>
                  </div>
                )}
              </div>

              <div className="px-6 py-4 border-t flex justify-between items-center">
                <div className="flex gap-2">
                  {TABS.map((t, i) => (
                    <button key={t.id} onClick={() => setTab(TABS[Math.max(0, i - 1)].id)}
                      className={`w-2 h-2 rounded-full ${tab === t.id ? 'bg-blue-700' : 'bg-gray-300'}`} />
                  ))}
                </div>
                <div className="flex gap-3">
                  <button onClick={() => { setMostraForm(false); setEditingId(null); }}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">Annulla</button>
                  <button onClick={handleSubmit}
                    className="px-4 py-2 bg-blue-700 text-white rounded text-sm hover:bg-blue-800">Salva</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ---- DETTAGLIO TESSERATO ---- */}
        {mostraDettaglio && dettaglio && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
              <div className="px-6 pt-6 pb-4 border-b flex justify-between items-start">
                <div className="flex items-center gap-4">
                  {dettaglio.foto_url && (
                    <img src={dettaglio.foto_url} alt="foto" className="w-14 h-14 rounded-full object-cover border-2 border-blue-200" />
                  )}
                  <div>
                    <h2 className="text-lg font-bold text-gray-800">{dettaglio.nome} {dettaglio.cognome}</h2>
                    <p className="text-sm text-gray-500 font-mono">{dettaglio.codice_fiscale}</p>
                  </div>
                </div>
                <button onClick={() => setMostraDettaglio(false)} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
              </div>

              <div className="overflow-y-auto px-6 py-4 flex-1 space-y-6">
                {/* Anagrafica */}
                <section>
                  <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Anagrafica</h3>
                  <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
                    {[
                      ['Data nascita', dettaglio.data_nascita],
                      ['Sesso', dettaglio.sesso],
                      ['Email', dettaglio.email],
                      ['Telefono', dettaglio.telefono],
                      ['Cellulare', dettaglio.cellulare],
                      ['Comune nascita', dettaglio.comune_nascita],
                      ['Provincia nascita', dettaglio.provincia_nascita],
                      ['Titolo studio', dettaglio.titolo_studio],
                    ].map(([label, value]) => value ? (
                      <div key={label as string}>
                        <span className="text-gray-400">{label}: </span>
                        <span className="text-gray-800">{value}</span>
                      </div>
                    ) : null)}
                    <div>
                      <span className="text-gray-400">Socio: </span>
                      <span className={dettaglio.e_socio ? 'text-green-600 font-medium' : 'text-gray-500'}>
                        {dettaglio.e_socio ? 'Sì' : 'No'}
                      </span>
                    </div>
                    {dettaglio.disabile && <div><span className="text-orange-600 text-xs font-medium">Disabile</span></div>}
                    {dettaglio.straniero && <div><span className="text-blue-600 text-xs font-medium">Straniero</span></div>}
                  </div>
                </section>

                {/* Residenza */}
                {(dettaglio.indirizzo || dettaglio.comune_residenza) && (
                  <section>
                    <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Residenza</h3>
                    <div className="text-sm text-gray-700 space-y-1">
                      {dettaglio.indirizzo && <p>{dettaglio.indirizzo}</p>}
                      {dettaglio.comune_residenza && (
                        <p>{dettaglio.cap_residenza} {dettaglio.comune_residenza} ({dettaglio.provincia_residenza}) {dettaglio.regione_residenza}</p>
                      )}
                    </div>
                  </section>
                )}

                {/* Tessera */}
                {(dettaglio.cod_tessera || dettaglio.categoria) && (
                  <section>
                    <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Dati tessera</h3>
                    <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
                      {[
                        ['Codice tessera', dettaglio.cod_tessera],
                        ['Tipo tessera', dettaglio.tipo_tessera],
                        ['Categoria', dettaglio.categoria],
                        ['Qualifica', dettaglio.qualifica],
                        ['Sport', dettaglio.sport],
                        ['Matricola', dettaglio.matricola],
                        ['Emissione', dettaglio.data_emissione_tessera],
                        ['Scadenza', dettaglio.data_scadenza_tessera],
                      ].map(([label, value]) => value ? (
                        <div key={label as string}>
                          <span className="text-gray-400">{label}: </span>
                          <span className={label === 'Scadenza' && new Date(value as string) < new Date() ? 'text-red-600 font-medium' : 'text-gray-800'}>
                            {value}
                          </span>
                        </div>
                      ) : null)}
                    </div>
                  </section>
                )}

                {/* Genitore */}
                {dettaglio.genitore && (
                  <section>
                    <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Genitore / Tutore</h3>
                    <div className="text-sm text-gray-700 space-y-1">
                      <p className="font-medium">{dettaglio.genitore.nome} {dettaglio.genitore.cognome}</p>
                      {dettaglio.genitore.email && <p>{dettaglio.genitore.email}</p>}
                      {dettaglio.genitore.telefono && <p>{dettaglio.genitore.telefono}</p>}
                    </div>
                  </section>
                )}

                {/* Documenti */}
                <section>
                  <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Documenti</h3>
                  {documentiDettaglio.length === 0 ? (
                    <p className="text-sm text-gray-400">Nessun documento caricato</p>
                  ) : (
                    <div className="space-y-2">
                      {documentiDettaglio.map(doc => (
                        <div key={doc.id} className="flex items-center justify-between bg-gray-50 rounded px-3 py-2">
                          <div>
                            <span className="text-xs font-medium bg-blue-100 text-blue-700 px-2 py-0.5 rounded mr-2">{doc.tipo}</span>
                            <a href={doc.url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline">
                              {doc.nome_file}
                            </a>
                            {doc.data_scadenza && <span className="text-xs text-gray-400 ml-2">scade: {doc.data_scadenza}</span>}
                          </div>
                          <button onClick={() => handleEliminaDocumento(doc.id)} className="text-red-400 hover:text-red-600 text-xs ml-4">
                            Elimina
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Upload documento */}
                  <div className="mt-4 border-t pt-4 space-y-3">
                    <p className="text-xs font-medium text-gray-600">Carica nuovo documento</p>
                    <div className="grid grid-cols-2 gap-3">
                      <input type="text" placeholder="Tipo (es. Certificato medico)" value={tipoDocumento}
                        onChange={e => setTipoDocumento(e.target.value)}
                        className="border border-gray-300 rounded px-3 py-2 text-sm" />
                      <input type="date" value={scadenzaDocumento} onChange={e => setScadenzaDocumento(e.target.value)}
                        className="border border-gray-300 rounded px-3 py-2 text-sm" />
                    </div>
                    <div className="flex items-center gap-3">
                      <input type="file" onChange={e => setFileDocumento(e.target.files?.[0] || null)} className="text-sm text-gray-600 flex-1" />
                      <button onClick={handleCaricaDocumento} disabled={caricandoDoc || !fileDocumento || !tipoDocumento}
                        className="px-3 py-2 bg-blue-700 text-white rounded text-sm hover:bg-blue-800 disabled:opacity-50 whitespace-nowrap">
                        {caricandoDoc ? 'Caricamento...' : 'Carica'}
                      </button>
                    </div>
                  </div>
                </section>
              </div>

              <div className="px-6 py-4 border-t flex justify-end gap-3">
                <button onClick={() => { setMostraDettaglio(false); apriModifica(dettaglio); }}
                  className="px-4 py-2 text-sm text-blue-600 hover:text-blue-800">Modifica</button>
                <button onClick={() => setMostraDettaglio(false)}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded text-sm hover:bg-gray-200">Chiudi</button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Tesserati;
