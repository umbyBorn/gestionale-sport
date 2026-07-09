--
-- PostgreSQL database dump
--

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg12+1)
-- Dumped by pg_dump version 18.4 (Ubuntu 18.4-0ubuntu0.26.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
--

-- *not* creating schema, since initdb creates it


--
--

CREATE TYPE public.metodopagamentoenum AS ENUM (
    'contanti',
    'bonifico',
    'altro'
);


--
--

CREATE TYPE public.ruoloenum AS ENUM (
    'amministratore',
    'staff',
    'commercialista',
    'tesserato',
    'genitore',
    'operatore'
);


--
--

CREATE TYPE public.statoassembleaenum AS ENUM (
    'pianificata',
    'conclusa',
    'annullata'
);


--
--

CREATE TYPE public.tipocontrattoenum AS ENUM (
    'sportivo',
    'amministrativo'
);


--
--

CREATE TYPE public.tipoeventoenum AS ENUM (
    'allenamento',
    'partita',
    'raduno',
    'altro'
);


--
--

CREATE TYPE public.tipomovimentoenum AS ENUM (
    'entrata',
    'uscita'
);


--
--

CREATE TYPE public.tiporapportoenum AS ENUM (
    'volontario',
    'cococo',
    'altro'
);


--
--

CREATE TYPE public.tipovotoenum AS ENUM (
    'favorevole',
    'contrario',
    'astenuto'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
--

CREATE TABLE public.assemblee (
    id integer NOT NULL,
    titolo character varying NOT NULL,
    data date NOT NULL,
    ora time without time zone,
    luogo character varying,
    stato public.statoassembleaenum NOT NULL,
    path_verbale character varying,
    note text
);


--
--

CREATE SEQUENCE public.assemblee_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.assemblee_id_seq OWNED BY public.assemblee.id;


--
--

CREATE TABLE public.compensi (
    id integer NOT NULL,
    staff_id integer NOT NULL,
    importo numeric(10,2) NOT NULL,
    data_erogazione date NOT NULL,
    descrizione character varying,
    path_autocertificazione character varying,
    totale_progressivo numeric(10,2) NOT NULL,
    soglia_superata boolean
);


--
--

CREATE SEQUENCE public.compensi_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.compensi_id_seq OWNED BY public.compensi.id;


--
--

CREATE TABLE public.contratti (
    id integer NOT NULL,
    staff_id integer NOT NULL,
    tipo public.tipocontrattoenum NOT NULL,
    data_inizio date NOT NULL,
    data_fine date,
    importo numeric(10,2) NOT NULL,
    path_pdf character varying,
    firmato boolean
);


--
--

CREATE SEQUENCE public.contratti_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.contratti_id_seq OWNED BY public.contratti.id;


--
--

CREATE TABLE public.dati_richiesta (
    id integer NOT NULL,
    modulo_id integer NOT NULL,
    stato character varying,
    nome character varying NOT NULL,
    cognome character varying NOT NULL,
    data_nascita character varying NOT NULL,
    codice_fiscale character varying,
    email character varying,
    telefono character varying,
    cellulare character varying,
    indirizzo character varying,
    comune_residenza character varying,
    provincia_residenza character varying,
    cap_residenza character varying,
    comune_nascita character varying,
    provincia_nascita character varying,
    stato_nascita character varying,
    sesso character varying,
    sport character varying,
    genitore_nome character varying,
    genitore_cognome character varying,
    genitore_email character varying,
    genitore_telefono character varying,
    genitore_documento_tipo character varying,
    genitore_documento_numero character varying,
    consenso_privacy boolean,
    data_invio character varying,
    note character varying
);


--
--

CREATE SEQUENCE public.dati_richiesta_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.dati_richiesta_id_seq OWNED BY public.dati_richiesta.id;


--
--

CREATE TABLE public.documenti (
    id integer NOT NULL,
    tesserato_id integer NOT NULL,
    tipo character varying NOT NULL,
    nome_file character varying NOT NULL,
    url character varying NOT NULL,
    data_scadenza date,
    note text
);


--
--

CREATE SEQUENCE public.documenti_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.documenti_id_seq OWNED BY public.documenti.id;


--
--

CREATE TABLE public.eventi (
    id integer NOT NULL,
    gruppo_id integer NOT NULL,
    tipo public.tipoeventoenum NOT NULL,
    titolo character varying NOT NULL,
    data date NOT NULL,
    ora_inizio time without time zone,
    ora_fine time without time zone,
    luogo character varying,
    note text,
    ricorrente_id integer
);


--
--

CREATE SEQUENCE public.eventi_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.eventi_id_seq OWNED BY public.eventi.id;


--
--

CREATE TABLE public.eventi_ricorrenti (
    id integer NOT NULL,
    gruppo_id integer NOT NULL,
    tipo public.tipoeventoenum DEFAULT 'allenamento'::public.tipoeventoenum NOT NULL,
    titolo character varying NOT NULL,
    ora_inizio time without time zone,
    ora_fine time without time zone,
    luogo character varying,
    giorni_settimana character varying NOT NULL,
    data_inizio date NOT NULL,
    data_fine date NOT NULL,
    attivo boolean DEFAULT true
);


--
--

CREATE SEQUENCE public.eventi_ricorrenti_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.eventi_ricorrenti_id_seq OWNED BY public.eventi_ricorrenti.id;


--
--

CREATE TABLE public.genitori (
    id integer NOT NULL,
    nome character varying NOT NULL,
    cognome character varying NOT NULL,
    email character varying,
    telefono character varying,
    documento_tipo character varying,
    documento_numero character varying
);


--
--

CREATE SEQUENCE public.genitori_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.genitori_id_seq OWNED BY public.genitori.id;


--
--

CREATE TABLE public.gruppi (
    id integer NOT NULL,
    nome character varying NOT NULL,
    descrizione character varying,
    attivo boolean
);


--
--

CREATE SEQUENCE public.gruppi_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.gruppi_id_seq OWNED BY public.gruppi.id;


--
--

CREATE TABLE public.gruppo_tesserato (
    id integer NOT NULL,
    gruppo_id integer NOT NULL,
    tesserato_id integer NOT NULL,
    data_iscrizione date NOT NULL
);


--
--

CREATE SEQUENCE public.gruppo_tesserato_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.gruppo_tesserato_id_seq OWNED BY public.gruppo_tesserato.id;


--
--

CREATE TABLE public.messaggi (
    id integer NOT NULL,
    intestazione character varying NOT NULL,
    corpo text NOT NULL,
    data_invio timestamp without time zone
);


--
--

CREATE TABLE public.messaggi_destinatari (
    id integer NOT NULL,
    messaggio_id integer NOT NULL,
    tesserato_id integer NOT NULL,
    letto boolean,
    email_inviata boolean
);


--
--

CREATE SEQUENCE public.messaggi_destinatari_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.messaggi_destinatari_id_seq OWNED BY public.messaggi_destinatari.id;


--
--

CREATE SEQUENCE public.messaggi_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.messaggi_id_seq OWNED BY public.messaggi.id;


--
--

CREATE TABLE public.movimenti_contabili (
    id integer NOT NULL,
    tipo public.tipomovimentoenum NOT NULL,
    data date NOT NULL,
    importo numeric(10,2) NOT NULL,
    descrizione character varying NOT NULL,
    categoria character varying,
    centro_costo character varying,
    intestatario character varying,
    allegato character varying,
    note text
);


--
--

CREATE SEQUENCE public.movimenti_contabili_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.movimenti_contabili_id_seq OWNED BY public.movimenti_contabili.id;


--
--

CREATE TABLE public.pagamenti (
    id integer NOT NULL,
    tesserato_id integer NOT NULL,
    tariffa_id integer NOT NULL,
    importo numeric(10,2) NOT NULL,
    data_scadenza date NOT NULL,
    data_pagamento date,
    metodo public.metodopagamentoenum,
    pagato boolean,
    contabile_allegata character varying
);


--
--

CREATE SEQUENCE public.pagamenti_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.pagamenti_id_seq OWNED BY public.pagamenti.id;


--
--

CREATE TABLE public.partecipazioni_assemblea (
    id integer NOT NULL,
    assemblea_id integer NOT NULL,
    tesserato_id integer NOT NULL,
    presente boolean,
    delega_a_id integer,
    voto public.tipovotoenum
);


--
--

CREATE SEQUENCE public.partecipazioni_assemblea_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.partecipazioni_assemblea_id_seq OWNED BY public.partecipazioni_assemblea.id;


--
--

CREATE TABLE public.permessi_operatore (
    id integer NOT NULL,
    utente_id integer NOT NULL,
    sezione character varying NOT NULL,
    abilitato boolean
);


--
--

CREATE SEQUENCE public.permessi_operatore_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.permessi_operatore_id_seq OWNED BY public.permessi_operatore.id;


--
--

CREATE TABLE public.presenze (
    id integer NOT NULL,
    evento_id integer NOT NULL,
    tesserato_id integer NOT NULL,
    presente boolean NOT NULL,
    note character varying
);


--
--

CREATE SEQUENCE public.presenze_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.presenze_id_seq OWNED BY public.presenze.id;


--
--

CREATE TABLE public.punti_ordine_giorno (
    id integer NOT NULL,
    assemblea_id integer NOT NULL,
    numero integer NOT NULL,
    titolo character varying NOT NULL,
    descrizione text,
    esito text
);


--
--

CREATE SEQUENCE public.punti_ordine_giorno_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.punti_ordine_giorno_id_seq OWNED BY public.punti_ordine_giorno.id;


--
--

CREATE TABLE public.push_subscriptions (
    id integer NOT NULL,
    utente_id integer,
    tesserato_id integer,
    endpoint character varying NOT NULL,
    p256dh character varying NOT NULL,
    auth character varying NOT NULL
);


--
--

CREATE SEQUENCE public.push_subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.push_subscriptions_id_seq OWNED BY public.push_subscriptions.id;


--
--

CREATE TABLE public.ricevute (
    id integer NOT NULL,
    pagamento_id integer NOT NULL,
    numero character varying NOT NULL,
    data_emissione date NOT NULL,
    intestatario character varying NOT NULL,
    importo numeric(10,2) NOT NULL,
    path_pdf character varying
);


--
--

CREATE SEQUENCE public.ricevute_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.ricevute_id_seq OWNED BY public.ricevute.id;


--
--

CREATE TABLE public.richieste_iscrizione (
    id integer NOT NULL,
    token character varying NOT NULL,
    nome_modulo character varying NOT NULL,
    attivo boolean,
    created_at character varying
);


--
--

CREATE SEQUENCE public.richieste_iscrizione_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.richieste_iscrizione_id_seq OWNED BY public.richieste_iscrizione.id;


--
--

CREATE TABLE public.staff (
    id integer NOT NULL,
    nome character varying NOT NULL,
    cognome character varying NOT NULL,
    data_nascita date NOT NULL,
    codice_fiscale character varying(16) NOT NULL,
    telefono character varying,
    email character varying,
    ruolo character varying NOT NULL,
    tipo_rapporto public.tiporapportoenum NOT NULL,
    data_inizio date NOT NULL,
    data_fine date,
    attivo boolean
);


--
--

CREATE TABLE public.staff_gruppo (
    id integer NOT NULL,
    staff_id integer NOT NULL,
    gruppo_id integer NOT NULL
);


--
--

CREATE SEQUENCE public.staff_gruppo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.staff_gruppo_id_seq OWNED BY public.staff_gruppo.id;


--
--

CREATE SEQUENCE public.staff_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.staff_id_seq OWNED BY public.staff.id;


--
--

CREATE TABLE public.tariffe (
    id integer NOT NULL,
    nome character varying NOT NULL,
    importo numeric(10,2) NOT NULL,
    categoria character varying,
    attiva boolean
);


--
--

CREATE SEQUENCE public.tariffe_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.tariffe_id_seq OWNED BY public.tariffe.id;


--
--

CREATE TABLE public.tesserati (
    id integer NOT NULL,
    utente_id integer,
    nome character varying NOT NULL,
    cognome character varying NOT NULL,
    data_nascita date NOT NULL,
    codice_fiscale character varying(16) NOT NULL,
    telefono character varying,
    indirizzo character varying,
    e_socio boolean,
    attivo boolean,
    genitore_id integer,
    sesso character varying(1),
    email character varying,
    cellulare character varying,
    comune_nascita character varying,
    provincia_nascita character varying,
    stato_nascita character varying,
    comune_residenza character varying,
    provincia_residenza character varying,
    regione_residenza character varying,
    cap_residenza character varying,
    cod_tessera character varying,
    tipo_tessera character varying,
    categoria character varying,
    qualifica character varying,
    sport character varying,
    data_emissione_tessera date,
    data_scadenza_tessera date,
    matricola character varying,
    disabile boolean,
    straniero boolean,
    titolo_studio character varying,
    foto_url character varying
);


--
--

CREATE SEQUENCE public.tesserati_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.tesserati_id_seq OWNED BY public.tesserati.id;


--
--

CREATE TABLE public.utenti (
    id integer NOT NULL,
    email character varying NOT NULL,
    password_hash character varying NOT NULL,
    ruolo public.ruoloenum NOT NULL,
    attivo boolean
);


--
--

CREATE SEQUENCE public.utenti_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
--

ALTER SEQUENCE public.utenti_id_seq OWNED BY public.utenti.id;


--
--

ALTER TABLE ONLY public.assemblee ALTER COLUMN id SET DEFAULT nextval('public.assemblee_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.compensi ALTER COLUMN id SET DEFAULT nextval('public.compensi_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.contratti ALTER COLUMN id SET DEFAULT nextval('public.contratti_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.dati_richiesta ALTER COLUMN id SET DEFAULT nextval('public.dati_richiesta_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.documenti ALTER COLUMN id SET DEFAULT nextval('public.documenti_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.eventi ALTER COLUMN id SET DEFAULT nextval('public.eventi_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.eventi_ricorrenti ALTER COLUMN id SET DEFAULT nextval('public.eventi_ricorrenti_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.genitori ALTER COLUMN id SET DEFAULT nextval('public.genitori_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.gruppi ALTER COLUMN id SET DEFAULT nextval('public.gruppi_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.gruppo_tesserato ALTER COLUMN id SET DEFAULT nextval('public.gruppo_tesserato_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.messaggi ALTER COLUMN id SET DEFAULT nextval('public.messaggi_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.messaggi_destinatari ALTER COLUMN id SET DEFAULT nextval('public.messaggi_destinatari_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.movimenti_contabili ALTER COLUMN id SET DEFAULT nextval('public.movimenti_contabili_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.pagamenti ALTER COLUMN id SET DEFAULT nextval('public.pagamenti_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.partecipazioni_assemblea ALTER COLUMN id SET DEFAULT nextval('public.partecipazioni_assemblea_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.permessi_operatore ALTER COLUMN id SET DEFAULT nextval('public.permessi_operatore_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.presenze ALTER COLUMN id SET DEFAULT nextval('public.presenze_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.punti_ordine_giorno ALTER COLUMN id SET DEFAULT nextval('public.punti_ordine_giorno_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.push_subscriptions ALTER COLUMN id SET DEFAULT nextval('public.push_subscriptions_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.ricevute ALTER COLUMN id SET DEFAULT nextval('public.ricevute_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.richieste_iscrizione ALTER COLUMN id SET DEFAULT nextval('public.richieste_iscrizione_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.staff ALTER COLUMN id SET DEFAULT nextval('public.staff_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.staff_gruppo ALTER COLUMN id SET DEFAULT nextval('public.staff_gruppo_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.tariffe ALTER COLUMN id SET DEFAULT nextval('public.tariffe_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.tesserati ALTER COLUMN id SET DEFAULT nextval('public.tesserati_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.utenti ALTER COLUMN id SET DEFAULT nextval('public.utenti_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.alembic_version (version_num) FROM stdin;
957aaca85b47
\.


--
-- Data for Name: assemblee; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.assemblee (id, titolo, data, ora, luogo, stato, path_verbale, note) FROM stdin;
\.


--
-- Data for Name: compensi; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.compensi (id, staff_id, importo, data_erogazione, descrizione, path_autocertificazione, totale_progressivo, soglia_superata) FROM stdin;
\.


--
-- Data for Name: contratti; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.contratti (id, staff_id, tipo, data_inizio, data_fine, importo, path_pdf, firmato) FROM stdin;
\.


--
-- Data for Name: dati_richiesta; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.dati_richiesta (id, modulo_id, stato, nome, cognome, data_nascita, codice_fiscale, email, telefono, cellulare, indirizzo, comune_residenza, provincia_residenza, cap_residenza, comune_nascita, provincia_nascita, stato_nascita, sesso, sport, genitore_nome, genitore_cognome, genitore_email, genitore_telefono, genitore_documento_tipo, genitore_documento_numero, consenso_privacy, data_invio, note) FROM stdin;
1	1	approvata	Julia	Roberts	1970-11-11	fdhdhdhdhdhdhhd	umberto.anguzza@gmail.com	3214234	42434	Via dell'orto 78	Catania	Catania	97899	Catania	Catania	Italia	F	PallaVolo							t	2026-07-06 18:24	
2	1	approvata	Julia	Roberts	2026-07-04											Italia			MArk	zugenberg					t	2026-07-06 18:56	
\.


--
-- Data for Name: documenti; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.documenti (id, tesserato_id, tipo, nome_file, url, data_scadenza, note) FROM stdin;
1	2	Certificato idoneità sportiva	certificati idoneita sportiva-12.pdf	https://res.cloudinary.com/srjdjqvl/image/upload/v1782909190/gestionale/tesserati/2/documenti/certificati%20idoneita%20sportiva-12.pdf.pdf	\N	\N
\.


--
-- Data for Name: eventi; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.eventi (id, gruppo_id, tipo, titolo, data, ora_inizio, ora_fine, luogo, note, ricorrente_id) FROM stdin;
1	1	allenamento	Allenamento test	2026-06-28	18:00:00	\N	Catania	\N	\N
2	1	allenamento	Allenamento under 12	2026-06-22	16:00:00	18:00:00	Catania	\N	1
3	1	allenamento	Allenamento under 12	2026-06-24	16:00:00	18:00:00	Catania	\N	1
4	1	allenamento	Allenamento under 12	2026-06-26	16:00:00	18:00:00	Catania	\N	1
5	1	allenamento	Allenamento under 12	2026-06-28	16:00:00	18:00:00	Catania	\N	1
6	1	allenamento	Allenamento under 12	2026-06-29	16:00:00	18:00:00	Catania	\N	1
7	1	allenamento	Allenamento under 12	2026-07-01	16:00:00	18:00:00	Catania	\N	1
8	1	allenamento	Allenamento under 12	2026-07-03	16:00:00	18:00:00	Catania	\N	1
9	1	allenamento	Allenamento under 12	2026-07-05	16:00:00	18:00:00	Catania	\N	1
10	1	allenamento	Allenamento under 12	2026-07-06	16:00:00	18:00:00	Catania	\N	1
11	1	allenamento	Allenamento under 12	2026-07-08	16:00:00	18:00:00	Catania	\N	1
12	1	allenamento	Allenamento under 12	2026-07-10	16:00:00	18:00:00	Catania	\N	1
13	1	allenamento	Allenamento under 12	2026-07-12	16:00:00	18:00:00	Catania	\N	1
14	1	allenamento	Allenamento under 12	2026-07-13	16:00:00	18:00:00	Catania	\N	1
15	1	allenamento	Allenamento under 12	2026-07-15	16:00:00	18:00:00	Catania	\N	1
16	1	allenamento	Allenamento under 12	2026-07-17	16:00:00	18:00:00	Catania	\N	1
17	1	allenamento	Allenamento under 12	2026-07-19	16:00:00	18:00:00	Catania	\N	1
18	1	allenamento	Allenamento under 12	2026-07-20	16:00:00	18:00:00	Catania	\N	1
19	1	allenamento	Allenamento under 12	2026-07-22	16:00:00	18:00:00	Catania	\N	1
21	1	allenamento	Allenamento under 12	2026-07-26	16:00:00	18:00:00	Catania	\N	1
22	1	allenamento	Allenamento under 12	2026-07-27	16:00:00	18:00:00	Catania	\N	1
23	1	allenamento	Allenamento under 12	2026-07-29	16:00:00	18:00:00	Catania	\N	1
24	1	allenamento	Allenamento under 12	2026-07-31	16:00:00	18:00:00	Catania	\N	1
25	1	allenamento	Allenamento under 12	2026-08-02	16:00:00	18:00:00	Catania	\N	1
26	1	allenamento	Allenamento under 12	2026-08-03	16:00:00	18:00:00	Catania	\N	1
27	1	allenamento	Allenamento under 12	2026-08-05	16:00:00	18:00:00	Catania	\N	1
28	1	allenamento	Allenamento under 12	2026-08-07	16:00:00	18:00:00	Catania	\N	1
29	1	allenamento	Allenamento under 12	2026-08-09	16:00:00	18:00:00	Catania	\N	1
30	1	allenamento	Allenamento under 12	2026-08-10	16:00:00	18:00:00	Catania	\N	1
31	1	allenamento	Allenamento under 12	2026-08-12	16:00:00	18:00:00	Catania	\N	1
32	1	allenamento	Allenamento under 12	2026-08-14	16:00:00	18:00:00	Catania	\N	1
33	1	allenamento	Allenamento under 12	2026-08-16	16:00:00	18:00:00	Catania	\N	1
34	1	allenamento	Allenamento under 12	2026-08-17	16:00:00	18:00:00	Catania	\N	1
35	1	allenamento	Allenamento under 12	2026-08-19	16:00:00	18:00:00	Catania	\N	1
36	1	allenamento	Allenamento under 12	2026-08-21	16:00:00	18:00:00	Catania	\N	1
37	1	allenamento	Allenamento under 12	2026-08-23	16:00:00	18:00:00	Catania	\N	1
38	1	allenamento	Allenamento under 12	2026-08-24	16:00:00	18:00:00	Catania	\N	1
39	1	allenamento	Allenamento under 12	2026-08-26	16:00:00	18:00:00	Catania	\N	1
40	1	allenamento	Allenamento under 12	2026-08-28	16:00:00	18:00:00	Catania	\N	1
41	1	allenamento	Allenamento under 12	2026-08-30	16:00:00	18:00:00	Catania	\N	1
42	1	allenamento	Allenamento under 12	2026-08-31	16:00:00	18:00:00	Catania	\N	1
43	1	allenamento	Allenamento under 12	2026-09-02	16:00:00	18:00:00	Catania	\N	1
44	1	allenamento	Allenamento under 12	2026-09-04	16:00:00	18:00:00	Catania	\N	1
45	1	allenamento	Allenamento under 12	2026-09-06	16:00:00	18:00:00	Catania	\N	1
46	1	allenamento	Allenamento under 12	2026-09-07	16:00:00	18:00:00	Catania	\N	1
47	1	allenamento	Allenamento under 12	2026-09-09	16:00:00	18:00:00	Catania	\N	1
48	1	allenamento	Allenamento under 12	2026-09-11	16:00:00	18:00:00	Catania	\N	1
49	1	allenamento	Allenamento under 12	2026-09-13	16:00:00	18:00:00	Catania	\N	1
50	1	allenamento	Allenamento under 12	2026-09-14	16:00:00	18:00:00	Catania	\N	1
51	1	allenamento	Allenamento under 12	2026-09-16	16:00:00	18:00:00	Catania	\N	1
52	1	allenamento	Allenamento under 12	2026-09-18	16:00:00	18:00:00	Catania	\N	1
53	1	allenamento	Allenamento under 12	2026-09-20	16:00:00	18:00:00	Catania	\N	1
54	1	allenamento	Allenamento under 12	2026-09-21	16:00:00	18:00:00	Catania	\N	1
55	1	allenamento	Allenamento under 12	2026-09-23	16:00:00	18:00:00	Catania	\N	1
56	1	allenamento	Allenamento under 12	2026-09-25	16:00:00	18:00:00	Catania	\N	1
57	1	allenamento	Allenamento under 12	2026-09-27	16:00:00	18:00:00	Catania	\N	1
58	1	allenamento	Allenamento under 12	2026-09-28	16:00:00	18:00:00	Catania	\N	1
59	1	allenamento	Allenamento under 12	2026-09-30	16:00:00	18:00:00	Catania	\N	1
60	1	allenamento	Allenamento under 12	2026-10-02	16:00:00	18:00:00	Catania	\N	1
61	1	allenamento	Allenamento under 12	2026-10-04	16:00:00	18:00:00	Catania	\N	1
62	1	allenamento	Allenamento under 12	2026-10-05	16:00:00	18:00:00	Catania	\N	1
63	1	allenamento	Allenamento under 12	2026-10-07	16:00:00	18:00:00	Catania	\N	1
64	1	allenamento	Allenamento under 12	2026-10-09	16:00:00	18:00:00	Catania	\N	1
65	1	allenamento	Allenamento under 12	2026-10-11	16:00:00	18:00:00	Catania	\N	1
66	1	allenamento	Allenamento under 12	2026-10-12	16:00:00	18:00:00	Catania	\N	1
67	1	allenamento	Allenamento under 12	2026-10-14	16:00:00	18:00:00	Catania	\N	1
68	1	allenamento	Allenamento under 12	2026-10-16	16:00:00	18:00:00	Catania	\N	1
69	1	allenamento	Allenamento under 12	2026-10-18	16:00:00	18:00:00	Catania	\N	1
70	1	allenamento	Allenamento under 12	2026-10-19	16:00:00	18:00:00	Catania	\N	1
71	1	allenamento	Allenamento under 12	2026-10-21	16:00:00	18:00:00	Catania	\N	1
72	1	allenamento	Allenamento under 12	2026-10-23	16:00:00	18:00:00	Catania	\N	1
73	1	allenamento	Allenamento under 12	2026-10-25	16:00:00	18:00:00	Catania	\N	1
74	1	allenamento	Allenamento under 12	2026-10-26	16:00:00	18:00:00	Catania	\N	1
75	1	allenamento	Allenamento under 12	2026-10-28	16:00:00	18:00:00	Catania	\N	1
76	1	allenamento	Allenamento under 12	2026-10-30	16:00:00	18:00:00	Catania	\N	1
77	1	allenamento	Allenamento under 12	2026-11-01	16:00:00	18:00:00	Catania	\N	1
78	1	allenamento	Allenamento under 12	2026-11-02	16:00:00	18:00:00	Catania	\N	1
79	1	allenamento	Allenamento under 12	2026-11-04	16:00:00	18:00:00	Catania	\N	1
80	1	allenamento	Allenamento under 12	2026-11-06	16:00:00	18:00:00	Catania	\N	1
81	1	allenamento	Allenamento under 12	2026-11-08	16:00:00	18:00:00	Catania	\N	1
82	1	allenamento	Allenamento under 12	2026-11-09	16:00:00	18:00:00	Catania	\N	1
83	1	allenamento	Allenamento under 12	2026-11-11	16:00:00	18:00:00	Catania	\N	1
84	1	allenamento	Allenamento under 12	2026-11-13	16:00:00	18:00:00	Catania	\N	1
85	1	allenamento	Allenamento under 12	2026-11-15	16:00:00	18:00:00	Catania	\N	1
86	1	allenamento	Allenamento under 12	2026-11-16	16:00:00	18:00:00	Catania	\N	1
87	1	allenamento	Allenamento under 12	2026-11-18	16:00:00	18:00:00	Catania	\N	1
88	1	allenamento	Allenamento under 12	2026-11-20	16:00:00	18:00:00	Catania	\N	1
89	1	allenamento	Allenamento under 12	2026-11-22	16:00:00	18:00:00	Catania	\N	1
90	1	allenamento	Allenamento under 12	2026-11-23	16:00:00	18:00:00	Catania	\N	1
91	1	allenamento	Allenamento under 12	2026-11-25	16:00:00	18:00:00	Catania	\N	1
92	1	allenamento	Allenamento under 12	2026-11-27	16:00:00	18:00:00	Catania	\N	1
93	1	allenamento	Allenamento under 12	2026-11-29	16:00:00	18:00:00	Catania	\N	1
94	1	allenamento	Allenamento under 12	2026-11-30	16:00:00	18:00:00	Catania	\N	1
95	1	allenamento	Allenamento under 12	2026-12-02	16:00:00	18:00:00	Catania	\N	1
96	1	allenamento	Allenamento under 12	2026-12-04	16:00:00	18:00:00	Catania	\N	1
97	1	allenamento	Allenamento under 12	2026-12-06	16:00:00	18:00:00	Catania	\N	1
98	1	allenamento	Allenamento under 12	2026-12-07	16:00:00	18:00:00	Catania	\N	1
99	1	allenamento	Allenamento under 12	2026-12-09	16:00:00	18:00:00	Catania	\N	1
100	1	allenamento	Allenamento under 12	2026-12-11	16:00:00	18:00:00	Catania	\N	1
101	1	allenamento	Allenamento under 12	2026-12-13	16:00:00	18:00:00	Catania	\N	1
102	1	allenamento	Allenamento under 12	2026-12-14	16:00:00	18:00:00	Catania	\N	1
103	1	allenamento	Allenamento under 12	2026-12-16	16:00:00	18:00:00	Catania	\N	1
104	1	allenamento	Allenamento under 12	2026-12-18	16:00:00	18:00:00	Catania	\N	1
105	1	allenamento	Allenamento under 12	2026-12-20	16:00:00	18:00:00	Catania	\N	1
106	1	allenamento	Allenamento under 12	2026-12-21	16:00:00	18:00:00	Catania	\N	1
107	1	allenamento	Allenamento under 12	2026-12-23	16:00:00	18:00:00	Catania	\N	1
108	1	allenamento	Allenamento under 12	2026-12-25	16:00:00	18:00:00	Catania	\N	1
109	1	allenamento	Allenamento under 12	2026-12-27	16:00:00	18:00:00	Catania	\N	1
110	1	allenamento	Allenamento under 12	2026-12-28	16:00:00	18:00:00	Catania	\N	1
112	2	allenamento	allenamento under 16	2026-07-01	18:00:00	19:30:00		\N	2
114	2	allenamento	allenamento under 16	2026-07-06	18:00:00	19:30:00		\N	2
115	2	allenamento	allenamento under 16	2026-07-08	18:00:00	19:30:00		\N	2
116	2	allenamento	allenamento under 16	2026-07-10	18:00:00	19:30:00		\N	2
117	2	allenamento	allenamento under 16	2026-07-13	18:00:00	19:30:00		\N	2
118	2	allenamento	allenamento under 16	2026-07-15	18:00:00	19:30:00		\N	2
119	2	allenamento	allenamento under 16	2026-07-17	18:00:00	19:30:00		\N	2
120	2	allenamento	allenamento under 16	2026-07-20	18:00:00	19:30:00		\N	2
121	2	allenamento	allenamento under 16	2026-07-22	18:00:00	19:30:00		\N	2
122	2	allenamento	allenamento under 16	2026-07-24	18:00:00	19:30:00		\N	2
123	2	allenamento	allenamento under 16	2026-07-27	18:00:00	19:30:00		\N	2
124	2	allenamento	allenamento under 16	2026-07-29	18:00:00	19:30:00		\N	2
125	2	allenamento	allenamento under 16	2026-07-31	18:00:00	19:30:00		\N	2
126	2	allenamento	allenamento under 16	2026-08-03	18:00:00	19:30:00		\N	2
127	2	allenamento	allenamento under 16	2026-08-05	18:00:00	19:30:00		\N	2
128	2	allenamento	allenamento under 16	2026-08-07	18:00:00	19:30:00		\N	2
129	2	allenamento	allenamento under 16	2026-08-10	18:00:00	19:30:00		\N	2
130	2	allenamento	allenamento under 16	2026-08-12	18:00:00	19:30:00		\N	2
131	2	allenamento	allenamento under 16	2026-08-14	18:00:00	19:30:00		\N	2
132	2	allenamento	allenamento under 16	2026-08-17	18:00:00	19:30:00		\N	2
133	2	allenamento	allenamento under 16	2026-08-19	18:00:00	19:30:00		\N	2
134	2	allenamento	allenamento under 16	2026-08-21	18:00:00	19:30:00		\N	2
135	2	allenamento	allenamento under 16	2026-08-24	18:00:00	19:30:00		\N	2
136	2	allenamento	allenamento under 16	2026-08-26	18:00:00	19:30:00		\N	2
137	2	allenamento	allenamento under 16	2026-08-28	18:00:00	19:30:00		\N	2
138	2	allenamento	allenamento under 16	2026-08-31	18:00:00	19:30:00		\N	2
139	2	allenamento	allenamento under 16	2026-09-02	18:00:00	19:30:00		\N	2
140	2	allenamento	allenamento under 16	2026-09-04	18:00:00	19:30:00		\N	2
141	2	allenamento	allenamento under 16	2026-09-07	18:00:00	19:30:00		\N	2
142	2	allenamento	allenamento under 16	2026-09-09	18:00:00	19:30:00		\N	2
143	2	allenamento	allenamento under 16	2026-09-11	18:00:00	19:30:00		\N	2
144	2	allenamento	allenamento under 16	2026-09-14	18:00:00	19:30:00		\N	2
145	2	allenamento	allenamento under 16	2026-09-16	18:00:00	19:30:00		\N	2
146	2	allenamento	allenamento under 16	2026-09-18	18:00:00	19:30:00		\N	2
147	2	allenamento	allenamento under 16	2026-09-21	18:00:00	19:30:00		\N	2
148	2	allenamento	allenamento under 16	2026-09-23	18:00:00	19:30:00		\N	2
149	2	allenamento	allenamento under 16	2026-09-25	18:00:00	19:30:00		\N	2
150	2	allenamento	allenamento under 16	2026-09-28	18:00:00	19:30:00		\N	2
151	2	allenamento	allenamento under 16	2026-09-30	18:00:00	19:30:00		\N	2
152	2	allenamento	allenamento under 16	2026-10-02	18:00:00	19:30:00		\N	2
153	2	allenamento	allenamento under 16	2026-10-05	18:00:00	19:30:00		\N	2
154	2	allenamento	allenamento under 16	2026-10-07	18:00:00	19:30:00		\N	2
155	2	allenamento	allenamento under 16	2026-10-09	18:00:00	19:30:00		\N	2
156	2	allenamento	allenamento under 16	2026-10-12	18:00:00	19:30:00		\N	2
157	2	allenamento	allenamento under 16	2026-10-14	18:00:00	19:30:00		\N	2
158	2	allenamento	allenamento under 16	2026-10-16	18:00:00	19:30:00		\N	2
159	2	allenamento	allenamento under 16	2026-10-19	18:00:00	19:30:00		\N	2
160	2	allenamento	allenamento under 16	2026-10-21	18:00:00	19:30:00		\N	2
161	2	allenamento	allenamento under 16	2026-10-23	18:00:00	19:30:00		\N	2
162	2	allenamento	allenamento under 16	2026-10-26	18:00:00	19:30:00		\N	2
163	2	allenamento	allenamento under 16	2026-10-28	18:00:00	19:30:00		\N	2
164	2	allenamento	allenamento under 16	2026-10-30	18:00:00	19:30:00		\N	2
165	2	allenamento	allenamento under 16	2026-11-02	18:00:00	19:30:00		\N	2
166	2	allenamento	allenamento under 16	2026-11-04	18:00:00	19:30:00		\N	2
167	2	allenamento	allenamento under 16	2026-11-06	18:00:00	19:30:00		\N	2
168	2	allenamento	allenamento under 16	2026-11-09	18:00:00	19:30:00		\N	2
169	2	allenamento	allenamento under 16	2026-11-11	18:00:00	19:30:00		\N	2
170	2	allenamento	allenamento under 16	2026-11-13	18:00:00	19:30:00		\N	2
171	2	allenamento	allenamento under 16	2026-11-16	18:00:00	19:30:00		\N	2
172	2	allenamento	allenamento under 16	2026-11-18	18:00:00	19:30:00		\N	2
173	2	allenamento	allenamento under 16	2026-11-20	18:00:00	19:30:00		\N	2
174	2	allenamento	allenamento under 16	2026-11-23	18:00:00	19:30:00		\N	2
175	2	allenamento	allenamento under 16	2026-11-25	18:00:00	19:30:00		\N	2
176	2	allenamento	allenamento under 16	2026-11-27	18:00:00	19:30:00		\N	2
177	2	allenamento	allenamento under 16	2026-11-30	18:00:00	19:30:00		\N	2
178	2	allenamento	allenamento under 16	2026-12-02	18:00:00	19:30:00		\N	2
179	2	allenamento	allenamento under 16	2026-12-04	18:00:00	19:30:00		\N	2
180	2	allenamento	allenamento under 16	2026-12-07	18:00:00	19:30:00		\N	2
181	2	allenamento	allenamento under 16	2026-12-09	18:00:00	19:30:00		\N	2
182	2	allenamento	allenamento under 16	2026-12-11	18:00:00	19:30:00		\N	2
183	2	allenamento	allenamento under 16	2026-12-14	18:00:00	19:30:00		\N	2
184	2	allenamento	allenamento under 16	2026-12-16	18:00:00	19:30:00		\N	2
185	2	allenamento	allenamento under 16	2026-12-18	18:00:00	19:30:00		\N	2
186	2	allenamento	allenamento under 16	2026-12-21	18:00:00	19:30:00		\N	2
187	2	allenamento	allenamento under 16	2026-12-23	18:00:00	19:30:00		\N	2
188	2	allenamento	allenamento under 16	2026-12-25	18:00:00	19:30:00		\N	2
189	2	allenamento	allenamento under 16	2026-12-28	18:00:00	19:30:00		\N	2
190	2	allenamento	allenamento under 16	2026-12-30	18:00:00	19:30:00		\N	2
191	2	partita	Test	2026-06-28	22:12:00	\N	Messina	\N	\N
192	1	altro	messa domenicale	2026-07-05	09:00:00	12:00:00	istituto	\N	3
193	1	altro	messa domenicale	2026-07-12	09:00:00	12:00:00	istituto	\N	3
194	1	altro	messa domenicale	2026-07-19	09:00:00	12:00:00	istituto	\N	3
195	1	altro	messa domenicale	2026-07-26	09:00:00	12:00:00	istituto	\N	3
196	1	altro	messa domenicale	2026-08-02	09:00:00	12:00:00	istituto	\N	3
197	1	altro	messa domenicale	2026-08-09	09:00:00	12:00:00	istituto	\N	3
198	1	altro	messa domenicale	2026-08-16	09:00:00	12:00:00	istituto	\N	3
199	1	altro	messa domenicale	2026-08-23	09:00:00	12:00:00	istituto	\N	3
200	1	altro	messa domenicale	2026-08-30	09:00:00	12:00:00	istituto	\N	3
\.


--
-- Data for Name: eventi_ricorrenti; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.eventi_ricorrenti (id, gruppo_id, tipo, titolo, ora_inizio, ora_fine, luogo, giorni_settimana, data_inizio, data_fine, attivo) FROM stdin;
1	1	allenamento	Allenamento under 12	16:00:00	18:00:00	Catania	[0, 2, 4, 6]	2026-06-22	2026-12-31	t
2	2	allenamento	allenamento under 16	18:00:00	19:30:00		[0, 2, 4]	2026-06-30	2026-12-31	t
3	1	altro	messa domenicale	09:00:00	12:00:00	istituto	[6]	2026-06-30	2026-08-30	t
\.


--
-- Data for Name: genitori; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.genitori (id, nome, cognome, email, telefono, documento_tipo, documento_numero) FROM stdin;
1	Umberto	Anguzza	umberto.anguzza@gmail.com			
2	MArk	zugenberg				
\.


--
-- Data for Name: gruppi; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.gruppi (id, nome, descrizione, attivo) FROM stdin;
1	Under 12	Under 12	t
2	under 16		t
3	Under 18	Under 18	t
4	Under 14	Under 14	t
5	Generico	Generico	t
6	Over 18	Over 18	t
7	Vice-Presidente	Vice-Presidente	t
\.


--
-- Data for Name: gruppo_tesserato; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.gruppo_tesserato (id, gruppo_id, tesserato_id, data_iscrizione) FROM stdin;
3	1	3	2026-06-30
4	3	110	2026-06-30
5	3	111	2026-06-30
6	4	112	2026-06-30
7	3	113	2026-06-30
8	4	114	2026-06-30
9	4	115	2026-06-30
10	4	116	2026-06-30
11	4	117	2026-06-30
12	5	118	2026-06-30
13	3	119	2026-06-30
14	4	120	2026-06-30
15	4	121	2026-06-30
16	4	122	2026-06-30
17	3	123	2026-06-30
18	6	124	2026-06-30
19	3	125	2026-06-30
20	7	126	2026-06-30
21	4	127	2026-06-30
22	4	128	2026-06-30
23	4	129	2026-06-30
24	3	130	2026-06-30
25	4	106	2026-07-01
26	3	102	2026-07-01
31	3	2	2026-07-01
32	5	147	2026-07-02
\.


--
-- Data for Name: messaggi; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.messaggi (id, intestazione, corpo, data_invio) FROM stdin;
1	test	test	2026-07-01 12:38:01.577014
2	test	test	2026-07-01 12:39:07.901848
3	test	test	2026-07-01 18:46:11.002432
4	test	test	2026-07-01 18:47:57.668637
5	test	test	2026-07-01 19:00:41.59165
6	Test	Test messaggio	2026-07-01 19:04:02.632212
7	test	test	2026-07-01 19:12:04.073366
8	test	test	2026-07-01 19:19:32.208023
9	test	test	2026-07-01 19:33:40.768719
10	test	test	2026-07-01 19:35:08.296876
11	test	test	2026-07-01 19:54:00.072205
12	test	test	2026-07-01 23:44:01.548237
13	test	test	2026-07-02 19:56:17.703019
14	test	test	2026-07-02 20:04:36.411203
15	test	test	2026-07-02 21:27:13.796226
16	test	test	2026-07-02 21:32:15.626237
17	test	test	2026-07-02 21:35:34.162372
18	test	test	2026-07-02 21:49:23.777898
19	Test	Test	2026-07-02 21:50:33.571362
20	Uyyyyyy	Hbggggy	2026-07-02 21:52:11.420311
21	23:53	02 luglio	2026-07-02 21:53:36.06037
22	test	test	2026-07-03 06:03:18.743973
23	test	test	2026-07-03 06:03:52.82205
24	Catania	Catania	2026-07-03 06:06:18.694083
25	Messaggio ore 21:33 del 3 luglio	Messaggio ore 21:33 del 3 luglio	2026-07-03 19:33:39.312998
26	messaggio 3 luglio 0re 21:48	messaggio 3 luglio 0re 21:48	2026-07-03 19:47:47.504025
27	test 21 59	test 21 59	2026-07-03 19:58:50.09108
28	aaa	aaa	2026-07-03 19:59:20.392613
29	bbb	bbbb	2026-07-03 20:00:10.853922
30	rtyryt	ryery	2026-07-03 20:02:24.098965
31	Catania	Catania	2026-07-04 03:16:12.711854
32	aaa	aaa	2026-07-05 11:56:12.080046
\.


--
-- Data for Name: messaggi_destinatari; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.messaggi_destinatari (id, messaggio_id, tesserato_id, letto, email_inviata) FROM stdin;
1	1	2	f	f
2	2	116	f	f
3	2	3	f	f
4	2	117	f	f
5	2	118	f	f
6	2	119	f	f
7	2	2	f	f
8	2	110	f	f
9	2	111	f	f
10	2	112	f	f
11	2	113	f	f
12	2	114	f	f
13	2	115	f	f
14	2	102	f	f
15	2	120	f	f
16	2	121	f	f
17	2	122	f	f
18	2	123	f	f
19	2	124	f	f
20	2	125	f	f
21	2	126	f	f
22	2	127	f	f
23	2	128	f	f
24	2	129	f	f
25	2	130	f	f
26	2	106	f	f
27	3	2	f	f
28	4	2	f	f
29	4	102	f	f
30	4	110	f	f
31	4	111	f	f
32	4	113	f	f
33	4	119	f	f
34	4	123	f	f
35	4	125	f	f
36	4	130	f	f
37	5	2	f	f
38	5	102	f	f
39	5	110	f	f
40	5	111	f	f
41	5	113	f	f
42	5	119	f	f
43	5	123	f	f
44	5	125	f	f
45	5	130	f	f
46	6	3	f	f
47	7	2	f	f
48	8	2	f	f
49	9	16	f	f
50	10	16	f	f
51	11	2	f	f
52	12	2	f	f
53	13	147	f	f
54	14	147	f	f
55	15	147	f	f
56	16	16	f	f
57	17	2	f	f
58	18	16	f	f
59	19	2	f	f
60	20	2	f	f
61	21	2	f	f
62	22	2	f	f
63	23	2	f	f
64	24	2	f	f
65	25	2	f	f
66	26	2	f	f
67	27	2	f	f
68	28	2	f	t
69	29	2	f	f
70	30	2	f	f
71	31	2	f	f
72	32	2	f	f
\.


--
-- Data for Name: movimenti_contabili; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.movimenti_contabili (id, tipo, data, importo, descrizione, categoria, centro_costo, intestatario, allegato, note) FROM stdin;
\.


--
-- Data for Name: pagamenti; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.pagamenti (id, tesserato_id, tariffa_id, importo, data_scadenza, data_pagamento, metodo, pagato, contabile_allegata) FROM stdin;
6	2	1	35.00	2026-06-28	2026-06-28	contanti	t	\N
\.


--
-- Data for Name: partecipazioni_assemblea; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.partecipazioni_assemblea (id, assemblea_id, tesserato_id, presente, delega_a_id, voto) FROM stdin;
\.


--
-- Data for Name: permessi_operatore; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.permessi_operatore (id, utente_id, sezione, abilitato) FROM stdin;
1	6	tesserati	t
2	6	gruppi	t
5	6	presenze	t
6	6	assemblee	t
7	6	calendario	t
8	6	messaggi	t
9	6	importazione	t
3	6	pagamenti	f
4	6	staff	f
\.


--
-- Data for Name: presenze; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.presenze (id, evento_id, tesserato_id, presente, note) FROM stdin;
3	116	4	t	\N
4	116	5	t	\N
5	116	6	t	\N
6	116	12	t	\N
7	116	13	t	\N
8	116	14	t	\N
9	116	2	t	\N
10	8	3	t	\N
11	9	2	t	\N
\.


--
-- Data for Name: punti_ordine_giorno; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.punti_ordine_giorno (id, assemblea_id, numero, titolo, descrizione, esito) FROM stdin;
\.


--
-- Data for Name: push_subscriptions; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.push_subscriptions (id, utente_id, tesserato_id, endpoint, p256dh, auth) FROM stdin;
\.


--
-- Data for Name: ricevute; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.ricevute (id, pagamento_id, numero, data_emissione, intestatario, importo, path_pdf) FROM stdin;
\.


--
-- Data for Name: richieste_iscrizione; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.richieste_iscrizione (id, token, nome_modulo, attivo, created_at) FROM stdin;
1	e5fefc446055499280e3b29a2b96e8b0	Iscrizione Pallavolo 2026-2027	t	2026-07-06 18:22
\.


--
-- Data for Name: staff; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.staff (id, nome, cognome, data_nascita, codice_fiscale, telefono, email, ruolo, tipo_rapporto, data_inizio, data_fine, attivo) FROM stdin;
\.


--
-- Data for Name: staff_gruppo; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.staff_gruppo (id, staff_id, gruppo_id) FROM stdin;
\.


--
-- Data for Name: tariffe; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.tariffe (id, nome, importo, categoria, attiva) FROM stdin;
1	Mensile pallavolo	40.00		t
\.


--
-- Data for Name: tesserati; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.tesserati (id, utente_id, nome, cognome, data_nascita, codice_fiscale, telefono, indirizzo, e_socio, attivo, genitore_id, sesso, email, cellulare, comune_nascita, provincia_nascita, stato_nascita, comune_residenza, provincia_residenza, regione_residenza, cap_residenza, cod_tessera, tipo_tessera, categoria, qualifica, sport, data_emissione_tessera, data_scadenza_tessera, matricola, disabile, straniero, titolo_studio, foto_url) FROM stdin;
116	\N	COSTANZA	GAMMAZZA	2013-03-31	TEMP_776DE32A	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	3140615	Atleta	Under 14	\N	Pallavolo	2025-09-22	\N	\N	f	f	\N	\N
3	\N	Mario	Rossi	2026-06-19		111111111		t	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4	\N	LUDOVICO	ADONIA	2013-10-11	DNALVC13R11C351S	\N	VIA GALERMO, 308	t	t	\N	M	sardomelinda@gmail.com	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	1923892	Ricreativo	Under 18	\N	Pallavolo	2026-06-07	2026-08-31	\N	f	f	\N	\N
5	\N	ARIANNA	AFFRONTO	2017-07-13	FFRRNN17L53C351J	\N	VIA LEUCATIA, 57	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	1923893	Ricreativo	Under 18	\N	Pallavolo	2026-06-07	2026-08-31	\N	f	f	\N	\N
6	\N	AZZURRA	AFFRONTO	2020-11-17	FFRZRR20S57C351Z	\N	VIA LEUCATIA, 57	t	t	\N	F	sardomelinda@gmail.com	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	1923894	Ricreativo	Under 18	\N	Pallavolo	2026-06-07	2026-08-31	\N	f	f	\N	\N
7	\N	SIMONA	AGLIOZZO	2013-08-21	GLZSMN13M61C351J	\N	VIA F. LAURANA 39	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3140594	Atleta	Under 14	\N	Pallavolo	2025-09-20	2026-08-31	\N	f	f	\N	\N
8	\N	MARTINA	ALBANO	2015-02-08	LBNMTN15B48C351C	\N	VIA C. DEL CARMINE, 5	t	t	\N	F	\N	\N	CATANIA	CT	\N	Tremestieri Etneo	Catania	Sicilia	950300	1923895	Ricreativo	Under 18	\N	DANZE ACCADEMICHE Danza Moderna e Contemporanea: Modern Jazz, Lyrical Jazz, Graham, Cunningam, Limon	2026-06-07	2026-08-31	\N	f	f	\N	\N
9	\N	BENEDETTA	ALBERONI	2010-09-11	LBRBDT10P51C351K	\N	VIA RENATO FUCINI ,8	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951260	3140595	Atleta	Under 18	\N	Pallavolo	2025-11-18	2026-08-31	\N	f	f	\N	\N
10	\N	EDOARDO	ALESSANDRELLO	2016-10-30	LSSDRD16R30C351C	\N	VIA F. GUGLIELMINO	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	1923896	Ricreativo	Under 18	\N	Futsal (calcio da sala - calcio a 5)	2026-06-07	2026-08-31	\N	f	f	\N	\N
11	\N	CHIARA	ALIBERTI	2014-10-05	LBRCHR14R45C351O	\N	VIA SASSARI, 66	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	1923897	Ricreativo	Under 18	\N	Pattinaggio artistico	2026-06-07	2026-08-31	\N	f	f	\N	\N
12	\N	BRANDO	AMORE	2017-08-31	MRABND17M31C351Y	\N	VIA PIETRO NOVELLI, 182	t	t	\N	M	\N	\N	CATANIA	CT	\N	Aci Bonaccorsi	Catania	Sicilia	951250	1923899	Ricreativo	Under 18	\N	Pallavolo	2026-06-07	2026-08-31	\N	f	f	\N	\N
13	\N	EDOARDO	AMORE	2019-05-21	MRADRD19E21C351G	\N	VIA PIETRO NOVELLI, 182	t	t	\N	M	\N	\N	CATANIA	CT	\N	Aci Bonaccorsi	Catania	Sicilia	951250	1923898	Ricreativo	Under 18	\N	Pallacanestro	2026-06-07	2026-08-31	\N	f	f	\N	\N
14	\N	MATTIA	ANASTASI	2019-11-01	NSTMTT19S01C351C	\N	VIA CORSO COLOMBO 54	t	t	\N	M	\N	\N	CATANIA	CT	\N	Trecastagni	Catania	Sicilia	950390	3165551	Atleta	Under 14	\N	Pallacanestro	2026-06-07	2026-08-31	\N	f	f	\N	\N
15	\N	GIOVANNI	ANGELINO	2018-05-03	NGLGNN18E03C351D	\N	VIA CRSTOFORO COLOMBO, 20	t	t	\N	M	\N	\N	CATANIA	CT	\N	San Gregorio di Catania	Catania	Sicilia	950270	3146178	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-18	2026-08-31	\N	f	f	\N	\N
17	\N	ALICE	ARCIDIACONO	2018-05-06	RCDLCA18E46C351F	\N	VIA COVIELLO, 37	t	t	\N	F	\N	\N	CATANIA	CT	\N	Aci Bonaccorsi	Catania	Sicilia	951000	1923900	Ricreativo	Under 18	\N	Pattinaggio artistico	2026-06-07	2026-08-31	\N	f	f	\N	\N
18	\N	COSTANZA	ARCIDIACONO	2018-05-06	RCDCTN18E46C351S	\N	VIA COVIELLO, 37	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	3165552	Atleta	Under 14	\N	Pattinaggio artistico	2026-06-07	2026-08-31	\N	f	f	\N	\N
19	\N	GIORGIA	ARENA	2013-10-21	RNAGRG13R61C351V	\N	VIA VAMPOLIERI, 34 M	t	t	\N	F	\N	\N	CATANIA	CT	\N	Aci Catena	Catania	Sicilia	950220	3165553	Atleta	Under 14	\N	Pallavolo	2026-06-07	2026-08-31	\N	f	f	\N	\N
20	\N	GIULIA	BARBERA	2019-05-07	BRBGLI19E47C351K	\N	VIA RICCARDO QUARTARARO, 11	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3165555	Atleta	Under 14	\N	Pattinaggio artistico	2026-06-07	2026-08-31	\N	f	f	\N	\N
21	\N	NICOLE	BERTINO	2011-01-12	BRTNCL11A52C351I	\N	VIA DEL BOSCO,269	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3140597	Atleta	Under 18	\N	Pallavolo	2025-09-20	2026-08-31	\N	f	f	\N	\N
22	\N	GIUSEPPE	BIVONA	2012-12-27	BVNGPP12T27C351K	\N	VIA DEL BOSCO 118	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951230	1923901	Ricreativo	Under 18	\N	Futsal (calcio da sala - calcio a 5)	2026-06-07	2026-08-31	\N	f	f	\N	\N
23	\N	ALESSIA	BLANDINI	2019-07-11	BLNLSS19L51C351A	\N	VIA LEUCATIA, 119	t	t	\N	F	\N	\N	CATANIA	CT	\N	Aci Bonaccorsi	Catania	Sicilia	951250	1923902	Ricreativo	Under 18	\N	Pattinaggio artistico	2026-06-07	2026-08-31	\N	f	f	\N	\N
24	\N	ALICE	BONACCORSO	2014-05-06	BNCLCA14E46C351C	\N	VIA GIACOMO LEOPARDI, 8	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	3165556	Atleta	Under 14	\N	Pattinaggio artistico	2026-06-07	2026-08-31	\N	f	f	\N	\N
25	\N	MARTINA	BONACCORSO	2015-12-28	BNCMTN15T68C351L	\N	VIA GIACOMO LEOPARDI, 80	t	t	\N	F	\N	\N	CATANIA	CT	\N	Aci Bonaccorsi	Catania	Sicilia	951250	3165558	Atleta	Under 14	\N	Pallavolo	2026-06-07	2026-08-31	\N	f	f	\N	\N
26	\N	ANDREA	BOZZO	2019-03-14	BZZNDR19C14C351T	\N	VIA RE MARTINO, 10	t	t	\N	M	\N	\N	CATANIA	CT	\N	Aci Bonaccorsi	Catania	Sicilia	951000	3165559	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-06-07	2026-08-31	\N	f	f	\N	\N
27	\N	SAMUELE	BUCCOLIERO	2018-09-23	BCCSML18P23C351K	\N	VIA ROSSO. SAN SECONDO	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	1923903	Ricreativo	Under 18	\N	Pallacanestro	2026-06-07	2026-08-31	\N	f	f	\N	\N
28	\N	SAMUELE	BUGLIO	2015-08-12	BGLSML15M12C351W	\N	VIA LUIGI CAPUANA, 67	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3143089	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-12	2026-08-31	\N	f	f	\N	\N
29	\N	VIOLA MARIA	CAMARDA	2012-06-04	CMRVMR12H44C351X	\N	VIA N. GIANNOTTA  103	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	1924546	Ricreativo	Under 18	\N	Pallavolo	2026-06-11	2026-08-31	\N	f	f	\N	\N
30	\N	FRANCESCA	CANDELIERI	2007-12-17	CNDFNC07T57C351G	\N	V.LE M. RAPISARDI 727	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951210	3140598	Atleta	Over 18	\N	Pallavolo	2025-11-18	2026-08-31	\N	f	f	\N	\N
31	\N	ANGELICA MARIA	CANNAVO'	2010-01-26	CNNNLC10A66C351P	\N	VIA ALLEGRIA,26	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	950300	3140599	Atleta	Under 18	\N	Pallavolo	2025-09-22	2026-08-31	\N	f	f	\N	\N
32	\N	TOMMASO	CAPIZZI	2018-10-09	CPZTMS18R09C351T	\N	VIA E LEOTTA ,8	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	3167571	Atleta	Under 14	\N	Pallacanestro	2026-06-11	2026-08-31	\N	f	f	\N	\N
33	\N	VITTORIA	CARPINTERI	2011-10-19	CRPVTR11R59C351W	\N	VIA ETNEA,9	t	t	\N	F	\N	\N	CATANIA	CT	\N	Gravina di Catania	Catania	Sicilia	950300	3140600	Atleta	Under 18	\N	Pallavolo	2025-09-20	2026-08-31	\N	f	f	\N	\N
34	\N	COSTANZA	CARRO	2017-11-21	CRRCTN17S61C351U	\N	VIA PUGLISI	t	t	\N	F	\N	\N	CATANIA	CT	\N	Scordia	Catania	Sicilia	950480	1924547	Ricreativo	Under 18	\N	Pallavolo	2026-06-11	2026-08-31	\N	f	f	\N	\N
35	\N	AURORA	CARUSO	2012-07-23	CRSRRA12L63C351O	\N	Via Tommasi di Lampedusa 15	t	t	\N	F	\N	\N	CATANIA	CT	\N	Trecastagni	Catania	Sicilia	950390	3140602	Atleta	Under 14	\N	Pallavolo	2025-09-22	2026-08-31	\N	f	f	\N	\N
36	\N	CARLOTTA	CARUSO	2015-07-19	CRSCLT15L59C351E	\N	VIAFRATELLI MAZAGLIA, 110	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	1924553	Ricreativo	Under 18	\N	DANZE ACCADEMICHE Danza Moderna e Contemporanea: Modern Jazz, Lyrical Jazz, Graham, Cunningam, Limon	2026-06-11	2026-08-31	\N	f	f	\N	\N
37	\N	CRISTINA	CATANIA	2015-08-05	CTNCST15M45E532M	\N	VIA CIMONE ,2A	t	t	\N	F	\N	\N	LENTINI	SR	\N	Catania	Catania	Sicilia	951250	1924562	Ricreativo	Under 18	\N	Pallavolo	2026-06-11	2026-08-31	\N	f	f	\N	\N
117	\N	CLAUDIO	GEMMA	2015-06-28	TEMP_5352AA91	\N	\N	t	t	\N	M	\N	\N	\N	\N	\N	\N	\N	\N	\N	3144190	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-16	\N	\N	f	f	\N	\N
118	\N	GIULIA	PANTALEONE	2005-09-02	TEMP_CA5E5477	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	2081795	Dirigente	Generico	\N	\N	2026-03-19	\N	\N	f	f	\N	\N
119	\N	BENEDETTA	PETITTO	2008-07-27	TEMP_BC550D7F	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	3140625	Atleta	Under 18	\N	Pallavolo	2025-11-18	\N	\N	f	f	\N	\N
38	\N	GIULIA	CATANIA	2017-05-10	CTNGLI17E50A028C	\N	VIAF. DELLACRETA, 118	t	t	\N	F	\N	\N	ACIREALE	CT	\N	Catania	Catania	Sicilia	951000	3167578	Atleta	Under 14	\N	Pattinaggio artistico	2026-06-11	2026-08-31	\N	f	f	\N	\N
39	\N	STELLA	CENTORBI	2008-09-03	CRTSLL08P43C351C	\N	n.coviello 28, Gravina di catania (CT) 28	t	t	\N	F	\N	\N	CATANIA	CT	\N	Gravina di Catania	Catania	Sicilia	951250	3140603	Atleta	Under 18	\N	Pallavolo	2025-09-20	2026-08-31	\N	f	f	\N	\N
40	\N	RUGGERO	CIANCITTO	2017-05-04	CNCRGR17E04E532S	\N	VIA MARCHE B	t	t	\N	M	\N	\N	LENTINI	SR	\N	San Giovanni la Punta	Catania	Sicilia	950370	3144064	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-14	2026-08-31	\N	f	f	\N	\N
41	\N	AURORA	CINO	2013-09-02	CNIRRA13P42C351N	\N	VIA NUOVALUCE, 61	t	t	\N	F	\N	\N	CATANIA	CT	\N	Tremestieri Etneo	Catania	Sicilia	950300	1924567	Ricreativo	Under 18	\N	DANZE ACCADEMICHE Danza Moderna e Contemporanea: Modern Jazz, Lyrical Jazz, Graham, Cunningam, Limon	2026-06-11	2026-08-31	\N	f	f	\N	\N
42	\N	BEATRICE	CIRINCIONE	2019-07-10	CRNBRC19L50C351I	\N	VIA SGROPPILLO, 7	t	t	\N	F	\N	\N	CATANIA	CT	\N	San Gregorio di Catania	Catania	Sicilia	950270	1924568	Ricreativo	Under 18	\N	Pattinaggio artistico	2026-06-11	2026-08-31	\N	f	f	\N	\N
43	\N	FRANCESCA  NICOLETTA	COCO	2011-09-07	CCOFNC11P47I754F	\N	VIA VENEZIA GIULIA ,31	t	t	\N	F	\N	\N	SIRACUSA	SR	\N	Catania	Catania	Sicilia	951000	3140604	Atleta	Under 18	\N	Pallavolo	2025-11-14	2026-08-31	\N	f	f	\N	\N
44	\N	UGO	COCO	2015-12-02	CCOGUO15T02C351O	\N	VIA DELLA SALLE	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	1924569	Ricreativo	Under 18	\N	Futsal (calcio da sala - calcio a 5)	2026-06-11	2026-08-31	\N	f	f	\N	\N
45	\N	GIUSEPPE ANTONINO	COMIS	1975-06-02	CMSGPP75H02C351H	\N	VIA GINO CERVI, 46	t	t	\N	M	\N	\N	CATANIA	CT	\N	Belpasso	Catania	Sicilia	950320	2081587	Dirigente	Tesoriere	\N	\N	2025-09-19	2026-08-31	\N	f	f	\N	\N
46	\N	LORENZO	COMMENDADORE	2016-06-09	CMMLNZ16H09C351T	\N	VIA NIZZETI, 18	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	1924572	Ricreativo	Under 18	\N	Futsal (calcio da sala - calcio a 5)	2026-06-11	2026-08-31	\N	f	f	\N	\N
47	\N	ANTONIO	COMPAGNINO	1977-05-06	CMPNTN77E06C351S	\N	VIALE MARIO RAPISARDI, 70	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	2081588	Dirigente	Segretario	\N	\N	2025-09-19	2026-08-31	\N	f	f	\N	\N
48	\N	DAVIDE	COMPAGNINO	2011-05-11	CMPDVD11E11C351J	\N	VIA OLBIA, 23	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	3155144	Atleta	Under 18	\N	Pallavolo	2026-04-25	2026-08-31	\N	f	f	\N	\N
49	\N	GIULIA	COMPAGNINO	2007-06-09	CMPGLI07H49C351Y	\N	VIA OLBIA 23	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3140607	Atleta	Over 18	\N	Pallavolo	2025-09-20	2026-08-31	\N	f	f	\N	\N
50	\N	GIULIA	CONSOLI	2012-09-10	CNSGLI12P50C351V	\N	VIA DEL BOSCO	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3140608	Atleta	Under 14	\N	Pallavolo	2025-09-20	2026-08-31	\N	f	f	\N	\N
51	\N	SOFIA	CONTI	2011-12-03	CNTSFO11T43C351N	\N	VIA BALATELLE, 18	t	t	\N	F	\N	\N	CATANIA	CT	\N	San Giovanni la Punta	Catania	Sicilia	950300	3140609	Atleta	Under 18	\N	Pallavolo	2025-11-19	2026-08-31	\N	f	f	\N	\N
52	\N	ANNA MARIAVITTORIA	CORSARO	2014-11-21	CRSNMR14S61C351O	\N	VIA ANTONIO SANT ANGELO FULCI	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	1924575	Ricreativo	Under 18	\N	Pallavolo	2026-06-11	2026-08-31	\N	f	f	\N	\N
53	\N	EMMA	CRISAFULLI	2014-08-01	CRSMME14M41C351E	\N	VIA RAVANUSA, 48	t	t	\N	F	\N	\N	CATANIA	CT	\N	Tremestieri Etneo	Catania	Sicilia	950300	1924576	Ricreativo	Under 18	\N	Pattinaggio artistico	2026-06-11	2026-08-31	\N	f	f	\N	\N
54	\N	ISABELLA	CURIALE	2017-03-18	CRLSLL17C58C351F	\N	VIA DELLA COSTITUZIONE, 19	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	1924579	Ricreativo	Under 18	\N	Pallavolo	2026-06-11	2026-08-31	\N	f	f	\N	\N
55	\N	SALVO	CURULLI	2017-06-16	CRLSLV17H16C351T	\N	VIA IV NOVEMBRE	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	1924580	Ricreativo	Under 18	\N	Futsal (calcio da sala - calcio a 5)	2026-06-11	2026-08-31	\N	f	f	\N	\N
56	\N	LORENZO	D AGOSTINO	2017-07-26	DGSLNZ17L26C351T	\N	VIA SAN GREGORIO, 3	t	t	\N	M	\N	\N	CATANIA	CT	\N	Sant'Agata li Battiati	Catania	Sicilia	950270	1925065	Ricreativo	Under 18	\N	Pallavolo	2026-06-19	2026-08-31	\N	f	f	\N	\N
57	\N	ANNA	D ALESSANDRO	2018-10-31	DLSNNA18R71C351W	\N	VIALE DELLA COSTITUZIONE 1, G	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	1925066	Ricreativo	Under 18	\N	Pallavolo	2026-06-19	2026-08-31	\N	f	f	\N	\N
58	\N	ANNA	D ALESSANDRO	2017-05-10	DLSNNA17E50C351V	\N	LARGO ENRICO MILLO, 3	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	1925067	Ricreativo	Under 18	\N	Futsal (calcio da sala - calcio a 5)	2026-06-19	2026-08-31	\N	f	f	\N	\N
59	\N	NICOLE	D ANGELO	2016-03-17	DNGNCL16C57C351H	\N	VIA DEI GIGLI, 15	t	t	\N	F	\N	\N	CATANIA	CT	\N	San Pietro Clarenza	Catania	Sicilia	951000	1925068	Ricreativo	Under 18	\N	DANZE ACCADEMICHE Danza Moderna e Contemporanea: Modern Jazz, Lyrical Jazz, Graham, Cunningam, Limon	2026-06-19	2026-08-31	\N	f	f	\N	\N
60	\N	AGATHEA	D ANTONIO	2020-06-02	DNTGTH20H42C351C	\N	VIA USTICA, 7	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	1925069	Ricreativo	Under 18	\N	DANZE ACCADEMICHE Danza Moderna e Contemporanea: Modern Jazz, Lyrical Jazz, Graham, Cunningam, Limon	2026-06-19	2026-08-31	\N	f	f	\N	\N
61	\N	PIETRO GABRIEL	D'ARRIGO	2016-05-31	DRRPRG16E31C351P	\N	VIA DEL CARAVAGGIO, 3	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3146180	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-18	2026-08-31	\N	f	f	\N	\N
62	\N	CLAUDIO	DE FRANCO	2016-05-01	DFRCLD16E01C351G	\N	VIA CONCETTO MARCHESI, 5	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3146289	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-19	2026-08-31	\N	f	f	\N	\N
63	\N	EDOARDO	DELL'ALI	2018-01-24	DLLDRD18A24C351S	\N	VIA EMPOLI,15	t	t	\N	M	\N	\N	CATANIA	CT	\N	San Giovanni la Punta	Catania	Sicilia	950300	3143200	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-13	2026-08-31	\N	f	f	\N	\N
64	\N	VIOLA	DI BELLA	2012-08-22	DBLVLI12M62C351M	\N	VIA C. MARCHESI  1/A	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3140610	Atleta	Under 14	\N	Pallavolo	2025-09-22	2026-08-31	\N	f	f	\N	\N
65	\N	MARGHERITA	DI CATALDO	2007-09-25	DCTMGH07P65C351X	\N	VIA PASSO GRAVINA	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	3140611	Atleta	Over 18	\N	Pallavolo	2025-09-20	2026-08-31	\N	f	f	\N	\N
66	\N	SIMONA	DI SALVATORE	1976-08-09	DSLSMN76M49C351C	\N	VIA OLBIA, 23	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	2082283	Dirigente	Generico	\N	\N	2026-04-25	2026-08-31	\N	f	f	\N	\N
67	\N	SIMONE ROBERTO	DI SALVO	2013-08-14	DSLSNR13M14C351Z	\N	VIA FRATELLI MAZZAGLIA 110	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3143092	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-12	2026-08-31	\N	f	f	\N	\N
68	\N	ROBERTA VITTORIA	FALLICA	2011-05-06	FLLRRT11E46C351L	\N	VIA ACICASTELLO,89	t	t	\N	F	\N	\N	CATANIA	CT	\N	Aci Castello	Catania	Sicilia	951000	3140612	Atleta	Under 18	\N	Pallavolo	2025-11-18	2026-08-31	\N	f	f	\N	\N
69	\N	SALVATORE	FICHERA	2017-08-20	FCHSVT17M20C351R	\N	VIA MESSINA, 9	t	t	\N	M	\N	\N	CATANIA	CT	\N	San Pietro Clarenza	Catania	Sicilia	950300	3144067	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-14	2026-08-31	\N	f	f	\N	\N
70	\N	COSTANZA	FULGI	2011-03-05	FLGCTN11C45C351B	\N	VIA A. BALDISERRA 55	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951230	3140614	Atleta	Under 18	\N	Pallavolo	2025-09-20	2026-08-31	\N	f	f	\N	\N
71	\N	ELENA	FULGI	2013-10-03	FLGLNE13R43C351G	\N	VIA A. BALDISERRA 54	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951230	3140613	Atleta	Under 14	\N	Pallavolo	2025-09-20	2026-08-31	\N	f	f	\N	\N
72	\N	COSTANZA	GAMUZZA	2013-03-31	GMZCTN13C71C351E	\N	VIA PIETRO DELL'OVA 388/B	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951230	3140615	Atleta	Under 14	\N	Pallavolo	2025-09-22	2026-08-31	\N	f	f	\N	\N
73	\N	CLAUDIO	GENNA	2015-06-28	GNNCLD15H28C351K	\N	VIA UMBERTO, 190	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	3144190	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-16	2026-08-31	\N	f	f	\N	\N
74	\N	FRANCESCO	GIULIANO	2018-12-11	GLNFNC18T11C351G	\N	VIA SAN GREGORIO, 31	t	t	\N	M	\N	\N	CATANIA	CT	\N	Aci Castello	Catania	Sicilia	950210	3146181	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-18	2026-08-31	\N	f	f	\N	\N
75	\N	JOHAN	GOVINDEN	2014-07-02	GVNJHN14L02C351S	\N	VIA DELLA PAGLIA  68	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951230	3143206	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-13	2026-08-31	\N	f	f	\N	\N
76	\N	ELISA	GRASSO	2011-10-05	GRSLSE11R45C351H	\N	VIA IDRIA, 31	t	t	\N	F	\N	\N	CATANIA	CT	\N	Aci Bonaccorsi	Catania	Sicilia	950300	3140616	Atleta	Under 18	\N	Pallavolo	2025-11-14	2026-08-31	\N	f	f	\N	\N
77	\N	SARA	GULLOTTA	2008-03-15	GLLSRA08C55C351Y	\N	Via Siena	t	t	\N	F	\N	\N	CATANIA	CT	\N	San Giovanni la Punta	Catania	Sicilia	950370	3140618	Atleta	Under 18	\N	Pallavolo	2025-09-20	2026-08-31	\N	f	f	\N	\N
78	\N	MICHELA	LA ROSA	2015-06-09	LRSMHL15H49C351E	\N	VIA LEUCATIA, 26	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3140619	Atleta	Under 14	\N	Pallavolo	2026-02-13	2026-08-31	\N	f	f	\N	\N
79	\N	MATTEO	LAGONA	2018-12-16	LGNMTT18T16C351X	\N	VIA VINCENZO MONCADA,18	t	t	\N	M	\N	\N	CATANIA	CT	\N	Sant'Agata li Battiati	Catania	Sicilia	950300	3143188	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-13	2026-08-31	\N	f	f	\N	\N
80	\N	ANDREA	LEONORA	2018-08-11	LNRNDR18M11C351Z	\N	VIA  FRATELLI  MAZZAGLIA 82/A	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3143078	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-12	2026-08-31	\N	f	f	\N	\N
81	\N	FRANCESCA	MANERI	2007-10-26	MNRFNC07R66C351N	\N	VIA PASSO GRAVINA 199	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	3140620	Atleta	Over 18	\N	Pallavolo	2025-09-22	2026-08-31	\N	f	f	\N	\N
82	\N	FRANCESCO	MARLETTA	2018-12-09	MRLFNC18T09C351T	\N	VIA BALATELLE, 19	t	t	\N	M	\N	\N	CATANIA	CT	\N	San Giovanni la Punta	Catania	Sicilia	950370	3144010	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-14	2026-08-31	\N	f	f	\N	\N
83	\N	MARCO	MASSIMINO	2007-02-11	MSSMRC07B11C351P	\N	VIA BARRIERA, 21	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	2081835	Dirigente	Generico	\N	\N	2026-03-20	2026-08-31	\N	f	f	\N	\N
84	\N	MICAELA	MESSINEO	2012-03-31	MSSMCL12C71C351A	\N	VIA LEUCATIA 131	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951230	3140621	Atleta	Under 14	\N	Pallavolo	2025-11-14	2026-08-31	\N	f	f	\N	\N
85	\N	GIUSEPPE	NAPOLI	1999-10-24	NPLGPP99R24C351W	\N	Via La Risa 102	t	t	\N	M	\N	\N	CATANIA	CT	\N	Pedara	Catania	Sicilia	950300	3140623	Atleta	Over 18	\N	Futsal (calcio da sala - calcio a 5)	2026-01-16	2026-08-31	\N	f	f	\N	\N
86	\N	GIULIA	PANEBIANCO	2005-09-02	PNBGLI05P42C351O	\N	VIALE EUROPA,74	t	t	\N	F	\N	\N	CATANIA	CT	\N	San Gregorio di Catania	Catania	Sicilia	950270	2081795	Dirigente	Generico	\N	\N	2026-03-18	2026-08-31	\N	f	f	\N	\N
87	\N	GIORDANA	PARISI	2012-02-21	PRSGDN12B61C351C	\N	VIA SAN FILIPPO NERI , 15	t	t	\N	F	\N	\N	CATANIA	CT	\N	Aci Castello	Catania	Sicilia	950210	3140624	Atleta	Under 18	\N	Pallavolo	2025-11-18	2026-08-31	\N	f	f	\N	\N
88	\N	BENEDETTA	PELLICCIA	2008-07-27	PLLBDT08L67C351R	\N	VIA .DA VINCI,6/B	t	t	\N	F	\N	\N	CATANIA	CT	\N	San Pietro Clarenza	Catania	Sicilia	951000	3140625	Atleta	Under 18	\N	Pallavolo	2025-11-18	2026-08-31	\N	f	f	\N	\N
89	\N	ELISA	PLATANIA	2012-04-24	PLTLSE12D64C351P	\N	VIA UNIONE EUROPEA 2	t	t	\N	F	\N	\N	CATANIA	CT	\N	Gravina di Catania	Catania	Sicilia	950300	3141178	Atleta	Under 14	\N	Pallavolo	2025-11-18	2026-08-31	\N	f	f	\N	\N
90	\N	ALICE	POLIZZI	2014-10-08	PLZLCA14R48C351Y	\N	VIA PIETRO NOVELLI,159	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3153601	Atleta	Under 14	\N	Pallavolo	2026-04-17	2026-08-31	\N	f	f	\N	\N
91	\N	MARTINA	PUGLIA	2008-06-25	PGLMTN08H65C351H	\N	VIA TEVERE, 20	t	t	\N	F	\N	\N	CATANIA	CT	\N	San Gregorio di Catania	Catania	Sicilia	950270	3140627	Atleta	Under 18	\N	Pallavolo	2025-09-22	2026-08-31	\N	f	f	\N	\N
92	\N	GABRIELE MARIA	RAGUSA	2015-09-12	RGSGRL15P12C351B	\N	VIA BARI,21	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3143194	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-13	2026-08-31	\N	f	f	\N	\N
93	\N	GIUSEPPE	RAGUSA	2009-08-01	RGSGPP09M01C351O	\N	VIA BARI, 21	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3143081	Atleta	Under 18	\N	Futsal (calcio da sala - calcio a 5)	2026-03-12	2026-08-31	\N	f	f	\N	\N
94	\N	GIUSEPPE AGATINO	RAGUSA	2010-10-10	RGSGPP10R10C351W	\N	VIA FOGGIA, 9	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3143086	Atleta	Under 18	\N	Futsal (calcio da sala - calcio a 5)	2026-03-12	2026-08-31	\N	f	f	\N	\N
95	\N	CLAUDIO ANGELO SENARATNE	RANPATI DEWAGE	2013-05-27	RNPCDN13E27C351N	\N	VIA TARANTO ,14	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3143197	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-13	2026-08-31	\N	f	f	\N	\N
96	\N	GIUSEPPE	SANTONOCITO	1975-06-22	SNTGPP75H22C351T	\N	Via Pietra Dell'ova	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	27119	Tecnici	Pallavolo	1° Livello	\N	2025-11-23	2026-08-31	\N	f	f	\N	\N
97	\N	MARIA	SANTONOCITO	2020-05-13	SNTMRA20E53E366N	\N	VIA PIETRO NOVELLI,159 A	t	t	\N	F	\N	\N	ISPICA	RG	\N	Catania	Catania	Sicilia	951250	3160095	Atleta	Under 14	\N	Pallavolo	2026-05-21	2026-08-31	\N	f	f	\N	\N
98	\N	CARMELA LINDA	SARDO	1979-11-10	SRDCML79S50C351V	\N	Via Pietra Dell'ova	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	2081585	Dirigente	Presidente	\N	\N	2025-09-19	2026-08-31	\N	f	f	\N	\N
99	\N	GIUSEPPE	SARDO	2003-07-28	SRDGPP03L28C351Z	\N	VIA LODI, 6	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951000	2081796	Dirigente	Generico	\N	\N	2026-03-18	2026-08-31	\N	f	f	\N	\N
100	\N	ANDREA	SCAMMACCA	2016-03-14	SCMNDR16C14C351A	\N	VIA TUBI TUBI, 7	t	t	\N	M	\N	\N	CATANIA	CT	\N	Aci Bonaccorsi	Catania	Sicilia	950200	3146182	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-18	2026-08-31	\N	f	f	\N	\N
101	\N	CARMEN MARIA	SCIUTO	2011-11-17	SCTCMN11S57C351G	\N	VIA LEUCATIA,125	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3140631	Atleta	Under 18	\N	Pallavolo	2025-11-18	2026-08-31	\N	f	f	\N	\N
103	\N	SONIA AGATA	SORBELLO	2007-08-30	SRBSGT07M70C351Z	\N	via della zagara 20, CT 20	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3140632	Atleta	Over 18	\N	Pallavolo	2025-09-22	2026-08-31	\N	f	f	\N	\N
104	\N	GIORGIA	TALLARICO	2009-02-27	TLLGRG09B67G371Y	\N	VIA DEL BOSCO , 167	t	t	\N	F	\N	\N	PATERNO'	CT	\N	Mascalucia	Catania	Sicilia	950300	3140635	Atleta	Under 18	\N	Pallavolo	2025-11-18	2026-08-31	\N	f	f	\N	\N
105	\N	MARIA GRAZIA	TRIPI	1978-08-09	TRPMGR78M49C351E	\N	Milano	t	t	\N	F	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951280	2081586	Dirigente	Vice-Presidente	\N	\N	2025-09-19	2026-08-31	\N	f	f	\N	\N
107	\N	DENUWAN ANGELO	UPASAKA LEKAMALAGE	2013-08-01	PSKDWN13M01C351S	\N	Vicolo Piccolo 6	t	t	\N	M	\N	\N	CATANIA	CT	\N	Catania	Catania	Sicilia	951250	3143203	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-13	2026-08-31	\N	f	f	\N	\N
108	\N	GINEVRA	ZAPPALA'	2012-03-02	ZPPGVR12C42C351A	\N	VIA IMOLA,5	t	t	\N	F	\N	\N	CATANIA	CT	\N	San Giovanni la Punta	Catania	Sicilia	950370	3140636	Atleta	Under 18	\N	Pallavolo	2025-11-18	2026-08-31	\N	f	f	\N	\N
109	\N	GRETA	ZUCCARA'	2009-08-05	ZCCGRT09M45C351S	\N	VIA CURROLO, 204	t	t	\N	F	\N	\N	CATANIA	CT	\N	Aci Bonaccorsi	Catania	Sicilia	951000	3140637	Atleta	Under 18	\N	Pallavolo	2025-09-22	2026-08-31	\N	f	f	\N	\N
110	\N	BENEDETTA	ALTAVILLA	2010-09-11	TEMP_2BB8CE86	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	3140595	Atleta	Under 18	\N	Pallavolo	2025-11-18	\N	\N	f	f	\N	\N
111	\N	STELLA	CENNARBI	2008-09-03	TEMP_20083CAB	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	3140603	Atleta	Under 18	\N	Pallavolo	2025-09-20	\N	\N	f	f	\N	\N
112	\N	RUGGERO	CIMOCITO	2017-05-04	TEMP_0745756C	\N	\N	t	t	\N	M	\N	\N	\N	\N	\N	\N	\N	\N	\N	3144064	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-14	\N	\N	f	f	\N	\N
113	\N	FRANCESCA NICOLETTA	COCO	2011-09-07	TEMP_3803C67B	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	3140604	Atleta	Under 18	\N	Pallavolo	2025-11-14	\N	\N	f	f	\N	\N
114	\N	GIULIA	CONTARDI	2012-09-10	TEMP_EDEBAD94	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	3140608	Atleta	Under 14	\N	Pallavolo	2025-09-20	\N	\N	f	f	\N	\N
115	\N	EDOARDO	DI BENEDETTO	2018-01-24	TEMP_AC5BD3A4	\N	\N	t	t	\N	M	\N	\N	\N	\N	\N	\N	\N	\N	\N	3143200	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-13	\N	\N	f	f	\N	\N
102	\N	CHIARA MARIA	SORBELLO	2008-11-04	SRBCRM08S44C351V		via della zagara 20, CT 20	t	t	\N	F			CATANIA	CT	Italia	Catania	Catania	Sicilia	951250	3140634	Atleta	Under 18		Pallavolo	2025-09-22	2026-08-31		f	f		\N
120	\N	ELISA	PIAZZA	2012-04-24	TEMP_7E750ACD	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	3141178	Atleta	Under 14	\N	Pallavolo	2025-11-18	\N	\N	f	f	\N	\N
121	\N	ALICE	POLIZZI	2014-10-08	TEMP_34FD287A	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	3153001	Atleta	Under 14	\N	Pallavolo	2026-04-17	\N	\N	f	f	\N	\N
122	\N	CLAUDIO ANGELO SENARATHNE	RANPATI DEWAGE	2013-05-27	TEMP_BE4807D6	\N	\N	t	t	\N	M	\N	\N	\N	\N	\N	\N	\N	\N	\N	3143197	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-13	\N	\N	f	f	\N	\N
123	\N	CHIARA MARIA	SORBELLO	2008-11-04	TEMP_A6C2DBFC	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	3140631	Atleta	Under 18	\N	Pallavolo	2025-11-18	\N	\N	f	f	\N	\N
124	\N	SONIA AGATA	SORBELLO	2007-08-30	TEMP_D7DC35F5	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	3140634	Atleta	Over 18	\N	Pallavolo	2025-09-22	\N	\N	f	f	\N	\N
125	\N	GIORGIA	TALLARICO	2009-02-27	TEMP_9C54E45B	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	3140632	Atleta	Under 18	\N	Pallavolo	2025-09-22	\N	\N	f	f	\N	\N
126	\N	MARIA GRAZIA	TRIPI	1978-08-09	TEMP_FE68D303	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	3140635	Dirigente	Vice-Presidente	\N	\N	2025-11-18	\N	\N	f	f	\N	\N
127	\N	ENEA RENEE BENEDETTO	TROMBETTA	2016-06-04	TEMP_22DDC75C	\N	\N	t	t	\N	M	\N	\N	\N	\N	\N	\N	\N	\N	\N	2081586	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2025-09-19	\N	\N	f	f	\N	\N
128	\N	DENUWAN ANGELO	UPASAKA LEKAMALAGE	2013-08-01	TEMP_4CEDC217	\N	\N	t	t	\N	M	\N	\N	\N	\N	\N	\N	\N	\N	\N	3143205	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-13	\N	\N	f	f	\N	\N
129	\N	GINEVRA	ZAPPALA'	2012-03-02	TEMP_B5FB7853	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	3143203	Atleta	Under 14	\N	Futsal (calcio da sala - calcio a 5)	2026-03-13	\N	\N	f	f	\N	\N
130	\N	GRETA	ZUCCARA'	2009-08-05	TEMP_B578B7F9	\N	\N	t	t	\N	F	\N	\N	\N	\N	\N	\N	\N	\N	\N	3140636	Atleta	Under 18	\N	Pallavolo	2025-11-18	\N	\N	f	f	\N	\N
106	\N	ENEA RENEE BENEDETTO	TROMBETTA	2016-06-04	TRMNNB16H04C351Z		VIA BARLETTA ,8	t	t	\N	M			CATANIA	CT	Italia	Catania	Catania	Sicilia	951250	3143205	Atleta	Under 14		Futsal (calcio da sala - calcio a 5)	2026-03-13	2026-08-31		f	f		\N
16	\N	MARIA CHIARA FRANCESCA	ANGUZZA	2009-01-08	NGZCRM09A48C351P	\N	VIA DELL'ORO,135	t	t	1	F	umberto.anguzza@gmail.com	\N	CATANIA	CT	Italia	Catania	Catania	Sicilia	951000	3140596	Atleta	Under 18	\N	Pallavolo	2025-09-20	2026-08-31	\N	f	f	\N	\N
2	5	Chiara Maria Francesca	Anguzza	2009-01-08	ngzcrm09a48c351p	3331234567	Via Dell’oro	t	t	1	\N	umberto.anguzza@gmail.com		\N	\N	Italia	Catania	Catania	\N	95123	\N	\N	\N	\N	PALLAVOLO	\N	\N	\N	f	f	\N	\N
147	7	Umberto	ANGUZZA	1972-11-23	ngzmrt72s23c351m	\N	\N	t	t	\N	\N	umberto.anguzza@gmail.com	\N	\N	\N	Italia	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	f	\N	\N
149	\N	Julia	Roberts	2026-07-04	1234567890987654	\N	\N	t	t	2	\N	\N	\N	\N	\N	Italia	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	f	\N	\N
\.


--
-- Data for Name: utenti; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.utenti (id, email, password_hash, ruolo, attivo) FROM stdin;
1	admin@gestionale.it	$2b$12$R9ihEM9W6Ar9hibav7M4DeKFFq73ffSXYKjnX5RblFIaYnGdCU2yS	amministratore	t
6	agnese.anguzza@gmail.com	$2b$12$/LAKCYwXg9EJmsOJbZHUOuI4GwAY/noGJo1/uojYfiVkIe4u5eC.u	operatore	t
5	umberto.anguzza@gmail.com	$2b$12$vadTBP/iQHjyk5jfjypib./Ah0fIT08bztkx3GW/qfuKW2/rskvyy	tesserato	t
7	umberto_anguzza@marina.difesa.it	$2b$12$tfzixHiiF2GpSaLzJpmau.xwJAmhKyvUUoiJHYlIGx52KUsF0s99W	tesserato	t
\.


--
--

SELECT pg_catalog.setval('public.assemblee_id_seq', 1, false);


--
--

SELECT pg_catalog.setval('public.compensi_id_seq', 1, false);


--
--

SELECT pg_catalog.setval('public.contratti_id_seq', 1, false);


--
--

SELECT pg_catalog.setval('public.dati_richiesta_id_seq', 2, true);


--
--

SELECT pg_catalog.setval('public.documenti_id_seq', 2, true);


--
--

SELECT pg_catalog.setval('public.eventi_id_seq', 200, true);


--
--

SELECT pg_catalog.setval('public.eventi_ricorrenti_id_seq', 3, true);


--
--

SELECT pg_catalog.setval('public.genitori_id_seq', 2, true);


--
--

SELECT pg_catalog.setval('public.gruppi_id_seq', 7, true);


--
--

SELECT pg_catalog.setval('public.gruppo_tesserato_id_seq', 32, true);


--
--

SELECT pg_catalog.setval('public.messaggi_destinatari_id_seq', 72, true);


--
--

SELECT pg_catalog.setval('public.messaggi_id_seq', 32, true);


--
--

SELECT pg_catalog.setval('public.movimenti_contabili_id_seq', 1, false);


--
--

SELECT pg_catalog.setval('public.pagamenti_id_seq', 6, true);


--
--

SELECT pg_catalog.setval('public.partecipazioni_assemblea_id_seq', 1, false);


--
--

SELECT pg_catalog.setval('public.permessi_operatore_id_seq', 9, true);


--
--

SELECT pg_catalog.setval('public.presenze_id_seq', 11, true);


--
--

SELECT pg_catalog.setval('public.punti_ordine_giorno_id_seq', 1, false);


--
--

SELECT pg_catalog.setval('public.push_subscriptions_id_seq', 2, true);


--
--

SELECT pg_catalog.setval('public.ricevute_id_seq', 1, false);


--
--

SELECT pg_catalog.setval('public.richieste_iscrizione_id_seq', 1, true);


--
--

SELECT pg_catalog.setval('public.staff_gruppo_id_seq', 1, false);


--
--

SELECT pg_catalog.setval('public.staff_id_seq', 1, false);


--
--

SELECT pg_catalog.setval('public.tariffe_id_seq', 1, true);


--
--

SELECT pg_catalog.setval('public.tesserati_id_seq', 149, true);


--
--

SELECT pg_catalog.setval('public.utenti_id_seq', 7, true);


--
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
--

ALTER TABLE ONLY public.assemblee
    ADD CONSTRAINT assemblee_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.compensi
    ADD CONSTRAINT compensi_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.contratti
    ADD CONSTRAINT contratti_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.dati_richiesta
    ADD CONSTRAINT dati_richiesta_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.documenti
    ADD CONSTRAINT documenti_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.eventi
    ADD CONSTRAINT eventi_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.eventi_ricorrenti
    ADD CONSTRAINT eventi_ricorrenti_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.genitori
    ADD CONSTRAINT genitori_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.gruppi
    ADD CONSTRAINT gruppi_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.gruppo_tesserato
    ADD CONSTRAINT gruppo_tesserato_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.messaggi_destinatari
    ADD CONSTRAINT messaggi_destinatari_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.messaggi
    ADD CONSTRAINT messaggi_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.movimenti_contabili
    ADD CONSTRAINT movimenti_contabili_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.pagamenti
    ADD CONSTRAINT pagamenti_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.partecipazioni_assemblea
    ADD CONSTRAINT partecipazioni_assemblea_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.permessi_operatore
    ADD CONSTRAINT permessi_operatore_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.presenze
    ADD CONSTRAINT presenze_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.punti_ordine_giorno
    ADD CONSTRAINT punti_ordine_giorno_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.push_subscriptions
    ADD CONSTRAINT push_subscriptions_endpoint_key UNIQUE (endpoint);


--
--

ALTER TABLE ONLY public.push_subscriptions
    ADD CONSTRAINT push_subscriptions_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.ricevute
    ADD CONSTRAINT ricevute_numero_key UNIQUE (numero);


--
--

ALTER TABLE ONLY public.ricevute
    ADD CONSTRAINT ricevute_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.richieste_iscrizione
    ADD CONSTRAINT richieste_iscrizione_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_codice_fiscale_key UNIQUE (codice_fiscale);


--
--

ALTER TABLE ONLY public.staff_gruppo
    ADD CONSTRAINT staff_gruppo_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.tariffe
    ADD CONSTRAINT tariffe_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.tesserati
    ADD CONSTRAINT tesserati_codice_fiscale_key UNIQUE (codice_fiscale);


--
--

ALTER TABLE ONLY public.tesserati
    ADD CONSTRAINT tesserati_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.utenti
    ADD CONSTRAINT utenti_pkey PRIMARY KEY (id);


--
--

CREATE INDEX ix_assemblee_id ON public.assemblee USING btree (id);


--
--

CREATE INDEX ix_compensi_id ON public.compensi USING btree (id);


--
--

CREATE INDEX ix_contratti_id ON public.contratti USING btree (id);


--
--

CREATE INDEX ix_dati_richiesta_id ON public.dati_richiesta USING btree (id);


--
--

CREATE INDEX ix_documenti_id ON public.documenti USING btree (id);


--
--

CREATE INDEX ix_eventi_id ON public.eventi USING btree (id);


--
--

CREATE INDEX ix_eventi_ricorrenti_id ON public.eventi_ricorrenti USING btree (id);


--
--

CREATE INDEX ix_genitori_id ON public.genitori USING btree (id);


--
--

CREATE INDEX ix_gruppi_id ON public.gruppi USING btree (id);


--
--

CREATE INDEX ix_gruppo_tesserato_id ON public.gruppo_tesserato USING btree (id);


--
--

CREATE INDEX ix_messaggi_destinatari_id ON public.messaggi_destinatari USING btree (id);


--
--

CREATE INDEX ix_messaggi_id ON public.messaggi USING btree (id);


--
--

CREATE INDEX ix_movimenti_contabili_id ON public.movimenti_contabili USING btree (id);


--
--

CREATE INDEX ix_pagamenti_id ON public.pagamenti USING btree (id);


--
--

CREATE INDEX ix_partecipazioni_assemblea_id ON public.partecipazioni_assemblea USING btree (id);


--
--

CREATE INDEX ix_permessi_operatore_id ON public.permessi_operatore USING btree (id);


--
--

CREATE INDEX ix_presenze_id ON public.presenze USING btree (id);


--
--

CREATE INDEX ix_punti_ordine_giorno_id ON public.punti_ordine_giorno USING btree (id);


--
--

CREATE INDEX ix_push_subscriptions_id ON public.push_subscriptions USING btree (id);


--
--

CREATE INDEX ix_ricevute_id ON public.ricevute USING btree (id);


--
--

CREATE INDEX ix_richieste_iscrizione_id ON public.richieste_iscrizione USING btree (id);


--
--

CREATE UNIQUE INDEX ix_richieste_iscrizione_token ON public.richieste_iscrizione USING btree (token);


--
--

CREATE INDEX ix_staff_gruppo_id ON public.staff_gruppo USING btree (id);


--
--

CREATE INDEX ix_staff_id ON public.staff USING btree (id);


--
--

CREATE INDEX ix_tariffe_id ON public.tariffe USING btree (id);


--
--

CREATE INDEX ix_tesserati_id ON public.tesserati USING btree (id);


--
--

CREATE UNIQUE INDEX ix_utenti_email ON public.utenti USING btree (email);


--
--

CREATE INDEX ix_utenti_id ON public.utenti USING btree (id);


--
--

ALTER TABLE ONLY public.compensi
    ADD CONSTRAINT compensi_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(id);


--
--

ALTER TABLE ONLY public.contratti
    ADD CONSTRAINT contratti_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(id);


--
--

ALTER TABLE ONLY public.dati_richiesta
    ADD CONSTRAINT dati_richiesta_modulo_id_fkey FOREIGN KEY (modulo_id) REFERENCES public.richieste_iscrizione(id);


--
--

ALTER TABLE ONLY public.documenti
    ADD CONSTRAINT documenti_tesserato_id_fkey FOREIGN KEY (tesserato_id) REFERENCES public.tesserati(id);


--
--

ALTER TABLE ONLY public.eventi
    ADD CONSTRAINT eventi_gruppo_id_fkey FOREIGN KEY (gruppo_id) REFERENCES public.gruppi(id);


--
--

ALTER TABLE ONLY public.eventi
    ADD CONSTRAINT eventi_ricorrente_id_fkey FOREIGN KEY (ricorrente_id) REFERENCES public.eventi_ricorrenti(id);


--
--

ALTER TABLE ONLY public.eventi_ricorrenti
    ADD CONSTRAINT eventi_ricorrenti_gruppo_id_fkey FOREIGN KEY (gruppo_id) REFERENCES public.gruppi(id);


--
--

ALTER TABLE ONLY public.gruppo_tesserato
    ADD CONSTRAINT gruppo_tesserato_gruppo_id_fkey FOREIGN KEY (gruppo_id) REFERENCES public.gruppi(id);


--
--

ALTER TABLE ONLY public.gruppo_tesserato
    ADD CONSTRAINT gruppo_tesserato_tesserato_id_fkey FOREIGN KEY (tesserato_id) REFERENCES public.tesserati(id);


--
--

ALTER TABLE ONLY public.messaggi_destinatari
    ADD CONSTRAINT messaggi_destinatari_messaggio_id_fkey FOREIGN KEY (messaggio_id) REFERENCES public.messaggi(id);


--
--

ALTER TABLE ONLY public.messaggi_destinatari
    ADD CONSTRAINT messaggi_destinatari_tesserato_id_fkey FOREIGN KEY (tesserato_id) REFERENCES public.tesserati(id);


--
--

ALTER TABLE ONLY public.pagamenti
    ADD CONSTRAINT pagamenti_tariffa_id_fkey FOREIGN KEY (tariffa_id) REFERENCES public.tariffe(id);


--
--

ALTER TABLE ONLY public.pagamenti
    ADD CONSTRAINT pagamenti_tesserato_id_fkey FOREIGN KEY (tesserato_id) REFERENCES public.tesserati(id);


--
--

ALTER TABLE ONLY public.partecipazioni_assemblea
    ADD CONSTRAINT partecipazioni_assemblea_assemblea_id_fkey FOREIGN KEY (assemblea_id) REFERENCES public.assemblee(id);


--
--

ALTER TABLE ONLY public.partecipazioni_assemblea
    ADD CONSTRAINT partecipazioni_assemblea_delega_a_id_fkey FOREIGN KEY (delega_a_id) REFERENCES public.tesserati(id);


--
--

ALTER TABLE ONLY public.partecipazioni_assemblea
    ADD CONSTRAINT partecipazioni_assemblea_tesserato_id_fkey FOREIGN KEY (tesserato_id) REFERENCES public.tesserati(id);


--
--

ALTER TABLE ONLY public.permessi_operatore
    ADD CONSTRAINT permessi_operatore_utente_id_fkey FOREIGN KEY (utente_id) REFERENCES public.utenti(id);


--
--

ALTER TABLE ONLY public.presenze
    ADD CONSTRAINT presenze_evento_id_fkey FOREIGN KEY (evento_id) REFERENCES public.eventi(id);


--
--

ALTER TABLE ONLY public.presenze
    ADD CONSTRAINT presenze_tesserato_id_fkey FOREIGN KEY (tesserato_id) REFERENCES public.tesserati(id);


--
--

ALTER TABLE ONLY public.punti_ordine_giorno
    ADD CONSTRAINT punti_ordine_giorno_assemblea_id_fkey FOREIGN KEY (assemblea_id) REFERENCES public.assemblee(id);


--
--

ALTER TABLE ONLY public.push_subscriptions
    ADD CONSTRAINT push_subscriptions_tesserato_id_fkey FOREIGN KEY (tesserato_id) REFERENCES public.tesserati(id);


--
--

ALTER TABLE ONLY public.push_subscriptions
    ADD CONSTRAINT push_subscriptions_utente_id_fkey FOREIGN KEY (utente_id) REFERENCES public.utenti(id);


--
--

ALTER TABLE ONLY public.ricevute
    ADD CONSTRAINT ricevute_pagamento_id_fkey FOREIGN KEY (pagamento_id) REFERENCES public.pagamenti(id);


--
--

ALTER TABLE ONLY public.staff_gruppo
    ADD CONSTRAINT staff_gruppo_gruppo_id_fkey FOREIGN KEY (gruppo_id) REFERENCES public.gruppi(id);


--
--

ALTER TABLE ONLY public.staff_gruppo
    ADD CONSTRAINT staff_gruppo_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staff(id);


--
--

ALTER TABLE ONLY public.tesserati
    ADD CONSTRAINT tesserati_genitore_id_fkey FOREIGN KEY (genitore_id) REFERENCES public.genitori(id);


--
--

ALTER TABLE ONLY public.tesserati
    ADD CONSTRAINT tesserati_utente_id_fkey FOREIGN KEY (utente_id) REFERENCES public.utenti(id);


--
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON SEQUENCES TO admin;


--
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON TYPES TO admin;


--
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON FUNCTIONS TO admin;


--
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO admin;


--
-- PostgreSQL database dump complete
--

