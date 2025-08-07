# Artificial QI – Manuale di Avvio 🧠⚙️

Piattaforma sviluppata dal gruppo **7Commits** per la valutazione delle prestazioni di LLM (Large Language Models).

## 👥 Componenti del Gruppo:
- **Marco Cola** - 2079237
- **Ruize Lin** - 2068236
- **Stefano Dal Poz** - 1204683
- **Giulia Hu** - 2009118
- **Mattia Piva** - 2008065
- **Giada Rossi** - 2045353

---

## 📦 Requisiti

> Puoi eseguire la webapp **con Docker** (consigliato) oppure **con Python + MySQL** in locale.

### 🔧 Requisiti comuni

- [x] **Git**
- [x] File `db.config` (creato da `db.config.example`)

---

### 📦 Requisiti per l’**esecuzione con Docker** (consigliato)

- [x] Docker ≥ 20.10  
- [x] Docker Compose

### 🐍 Requisiti per l’**esecuzione con Python**

- [x] Python ≥ 3.10  
- [x] MySQL ≥ 5.7  
- [x] `pip install -r requirements.txt`

---

## 📁 Clonazione del progetto

```bash
git clone https://github.com/7Commits/MVP
cd MVP
cp db.config.example db.config

```

## 🐳 Avvio con Docker

Assicurati che il file db.config contenga:
```bash
[mysql]
user = root
password = root
host = db
port = 3306
database = llm_platform
```

poi esegui:
```bash
docker compose up -d --build
```

infine accedi alla webapp:
```bash
http://localhost:8501
```

## 🛑 Arresto dell'app (Docker)

Per mettere in pausa:

```bash
docker compose stop
```

Per spegnere e rimuovere:

```bash
docker compose down
```

## 🐍 Avvio con Python + MySQL locale

1. Avvia il tuo server MySQL locale (con porta, user e password compatibili)

2. Modifica db.config così:
```bash
[mysql]
user = tuo_user
password = tua_password
host = localhost
port = 3306
database = llm_platform
```
3. Installa le dipendenze Python:
```bash
pip install -r requirements.txt
```

4. Avvia l'app con:
```bash
python -m streamlit run app.py --server.port 8501
```

# 🧪 Guida all’Uso dell’Applicazione

## 🏠 Pagina Home

La pagina iniziale della webapp mostra una descrizione dell’app e un menu laterale con le varie sezioni disponibili.

---

## ⚙️ Configurazione API

In questa sezione puoi creare dei **preset** di connessione per i vari LLM, inserendo:

- Nome del preset
- Chiave API
- Endpoint del provider (URL)
- Modello da utilizzare
- Temperatura di generazione

Puoi salvare, modificare o eliminare preset già configurati.

---

## ❓ Gestione Domande

Qui puoi gestire le **domande e risposte attese**:

- Inserire manualmente domanda e risposta
- Modificare o eliminare una voce
- Importare un file `.csv` o `.json` con domande e risposte attese

### 📄 Formato richiesto per importazione

```csv
domanda,risposta_attesa,categoria (opzionale)
Qual è la capitale d'Italia?,Roma,Geografia
Chi ha scritto '1984'?,George Orwell,Letteratura
```

## 💬 Supporto tecnico

In caso di problemi o domande, contattare:

- 📧 Email: [7commits@gmail.com](mailto:7commits@gmail.com)

Inserendo eventuali messaggi di errore e una breve descrizione del problema.










