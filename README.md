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
host=db
user=root
password=
database=llm_platform
port=3306
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
host=localhost
user=root
password=your_password_here
database=llm_platform
port=3306
ssl_ca=
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

- Inserire manualmente domanda e risposta, oppure set di domande e risposte
- Modificare o eliminare una voce
- Importare un file `.csv` o `.json` con domande e risposte attese

### 📄 Esempio di formato richiesto per importazione domande e risposte CSV
Deve includere le colonne 'domanda' e 'risposta_attesa'. Può includere opzionalmente 'categoria'.
```csv
domanda,risposta_attesa,categoria
"Quanto fa 2+2?","4","Matematica Base"
"Qual è la capitale della Francia?","Parigi","Geografia"
"Chi ha scritto 'Amleto'?","William Shakespeare","Letteratura"
```

### 📄 Esempio di formato richiesto per importazione domande e risposte JSON
Deve contenere un array di oggetti con i campi 'domanda' e 'risposta_attesa'. Può includere opzionalmente 'categoria'.
```json
[
    {
        "domanda": "Quanto fa 2+2?",
        "risposta_attesa": "4",
        "categoria": "Matematica Base"
    },
    {
        "domanda": "Qual è la capitale della Francia?",
        "risposta_attesa": "Parigi",
        "categoria": "Geografia"
    },
    {
        "domanda": "Chi ha scritto 'Romeo e Giulietta'?",
        "risposta_attesa": "William Shakespeare"
    }
]
```

### 📄 Esempio di formato richiesto per importazione set di domande e risposte CSV
Ogni riga deve contenere le colonne name (nome del set), id (ID della domanda), domanda (testo), risposta_attesa e categoria.
```csv
name,id,domanda,risposta_attesa,categoria
Capitali,1,Qual è la capitale della Francia?,Parigi,Geografia
Capitali,2,Qual è la capitale della Germania?,Berlino,Geografia
Matematica Base,3,Quanto fa 2+2?,4,Matematica
Matematica Base,4,Quanto fa 10*4?,40,Matematica
```


### 📄 Esempio di formato richiesto per importazione set di domande e risposte JSON

```json
[
    {
        "name": "Capitali",
        "questions": [
            {
                "id": "1",
                "domanda": "Qual è la capitale della Francia?",
                "risposta_attesa": "Parigi",
                "categoria": "Geografia"
            },
            {
                "id": "2",
                "domanda": "Qual è la capitale della Germania?",
                "risposta_attesa": "Berlino",
                "categoria": "Geografia"
            }
        ]
    },
    {
        "name": "Matematica Base",
        "questions": [
            {
                "id": "3",
                "domanda": "Quanto fa 2+2?",
                "risposta_attesa": "4",
                "categoria": "Matematica"
            },
            {
                "id": "4",
                "domanda": "Quanto fa 10*4?",
                "risposta_attesa": "40",
                "categoria": "Matematica"
            }
        ]
    }
]
```
#### Note importazione:

- Se una domanda con lo stesso ID esiste già, non verrà aggiunta nuovamente
- Se un set con lo stesso nome esiste già, verrà saltato
- Solo le domande nuove verranno aggiunte al database
- Le domande esistenti verranno referenziate nei nuovi set


## 💬 Supporto tecnico

In caso di problemi o domande, contattare:

- 📧 Email: [7commits@gmail.com](mailto:7commits@gmail.com)

Inserendo eventuali messaggi di errore e una breve descrizione del problema.










