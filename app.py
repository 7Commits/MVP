import streamlit as st
import os
import importlib
import sys
import logging
from logging_config import setup_logging

setup_logging()
logging.info("Applicazione avviata")

from models.db_utils import init_db
from controllers.question_controller import load_questions
from controllers.question_set_controller import load_sets
from controllers.test_controller import load_results

# Imposta la configurazione della pagina
st.set_page_config(
    page_title="LLM Test Evaluation Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inizializza lo stato della sessione
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# Inizializza i file di dati se non esistono
if not st.session_state.initialized:
    init_db()
    st.session_state.initialized = True

# Carica i dati nello stato della sessione se non sono già caricati
if 'questions' not in st.session_state:
    st.session_state.questions = load_questions()

if 'question_sets' not in st.session_state:
    st.session_state.question_sets = load_sets()

if 'results' not in st.session_state:
    st.session_state.results = load_results()

# Configurazione API
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.environ.get('OPENAI_API_KEY', '')

if 'endpoint' not in st.session_state:
    st.session_state.endpoint = 'https://api.openai.com/v1'

if 'model' not in st.session_state:
    st.session_state.model = 'gpt-4o'

if 'temperature' not in st.session_state:
    st.session_state.temperature = 0.0

if 'max_tokens' not in st.session_state:
    st.session_state.max_tokens = 1000

# Applicazione principale
st.title("🧠 LLM Test Evaluation Platform - Artificial QI")

# Importa utilità UI
from view.style_utils import add_global_styles, add_page_header

# Aggiungi CSS personalizzato e stili globali
add_global_styles()

# Definisce le pagine disponibili e il menu laterale
PAGES = {
    "Home": None,
    "Configurazione API": "view.api_configurazione",
    "Gestione Domande": "view.gestione_domande",
    "Gestione Set di Domande": "view.gestione_set",
    "Esecuzione Test": "view.esecuzione_test",
    "Visualizzazione Risultati": "view.visualizza_risultati",
}

selected_page = st.sidebar.radio("Navigazione", list(PAGES.keys()))


# CSS Estremo per Visibilità Input in Tema Scuro
st.markdown("""
<style>
    /* TEMA SCURO: Input con sfondo CHIARO e testo NERO */
    [data-theme="dark"] div[data-testid="stTextInput"] input,
    .streamlit-dark div[data-testid="stTextInput"] input,
    [data-theme="dark"] div[data-baseweb="input"] input,
    .streamlit-dark div[data-baseweb="input"] input,
    [data-theme="dark"] div[data-testid="stTextArea"] textarea,
    .streamlit-dark div[data-testid="stTextArea"] textarea,
    [data-theme="dark"] div[data-baseweb="textarea"] textarea,
    .streamlit-dark div[data-baseweb="textarea"] textarea,
    [data-theme="dark"] div[data-testid="stNumberInput"] input,
    .streamlit-dark div[data-testid="stNumberInput"] input {
        color: #000000 !important; /* Testo NERO */
        background-color: #FFFFFF !important; /* Sfondo BIANCO */
        border: 1px solid #AAAAAA !important; /* Bordo grigio chiaro */
    }

    /* TEMA SCURO: Select box con testo NERO su sfondo BIANCO */
    /* Nota: lo stile dei select è più complesso da sovrascrivere completamente */
    [data-theme="dark"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    .streamlit-dark div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        color: #000000 !important;
        background-color: #FFFFFF !important;
        border: 1px solid #AAAAAA !important;
    }
    [data-theme="dark"] div[data-testid="stSelectbox"] svg,
    .streamlit-dark div[data-testid="stSelectbox"] svg {
        fill: #000000 !important; /* Icona freccia nera */
    }

    /* TEMA CHIARO: Input con sfondo BIANCO e testo NERO (standard) */
    [data-theme="light"] div[data-testid="stTextInput"] input,
    .streamlit-light div[data-testid="stTextInput"] input,
    [data-theme="light"] div[data-baseweb="input"] input,
    .streamlit-light div[data-baseweb="input"] input,
    [data-theme="light"] div[data-testid="stTextArea"] textarea,
    .streamlit-light div[data-testid="stTextArea"] textarea,
    [data-theme="light"] div[data-baseweb="textarea"] textarea,
    .streamlit-light div[data-baseweb="textarea"] textarea,
    [data-theme="light"] div[data-testid="stNumberInput"] input,
    .streamlit-light div[data-testid="stNumberInput"] input {
        color: #000000 !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
    }

    [data-theme="light"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    .streamlit-light div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        color: #000000 !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
    }
    [data-theme="light"] div[data-testid="stSelectbox"] svg,
    .streamlit-light div[data-testid="stSelectbox"] svg {
        fill: #000000 !important;
    }

    /* Stili generali per tutti i componenti input (bordi, padding) */
    div[data-testid="stTextInput"] input,
    div[data-baseweb="input"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-baseweb="textarea"] textarea,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border-radius: 4px !important;
    }
    /* Mostra interamente il testo selezionato senza troncamento */
    div[data-baseweb="select"] * {
        white-space: normal !important;
    }

    /* Stili per i box delle funzionalità (mantenuti dal codice originale) */
    .feature-box {
        background-color: white;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 25px;
        border-top: 4px solid #4F6AF0;
        box-shadow: 0 6px 18px rgba(79, 106, 240, 0.1);
        transition: all 0.3s ease;
    }
    .feature-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(79, 106, 240, 0.15);
    }
    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 15px;
        color: #333;
        display: flex;
        align-items: center;
    }
    .feature-description {
        font-size: 1rem;
        color: #555;
        line-height: 1.5;
    }
    .icon-large {
        font-size: 2rem;
        margin-right: 0.75rem;
        background: linear-gradient(135deg, #F0F4FF, #E6EBFF);
        width: 50px;
        height: 50px;
        line-height: 50px;
        text-align: center;
        border-radius: 50%;
        box-shadow: 0 4px 10px rgba(79, 106, 240, 0.1);
    }
    .welcome-section {
        margin-bottom: 2.5rem;
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #4F6AF0;
    }
    .welcome-title {
        font-size: 2.2rem;
        font-weight: bold;
        color: #4F6AF0;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.3rem;
        color: #555;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    .getting-started {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        margin-top: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.05);
        border-left: 5px solid #4F6AF0;
    }
    .getting-started h3 {
        color: #4F6AF0;
        margin-bottom: 1rem;
    }
    .getting-started ol {
        padding-left: 1.5rem;
    }
    .getting-started li {
        margin-bottom: 0.75rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)


def show_home_page():
    """Visualizza la pagina principale con le funzionalità della piattaforma."""

    st.markdown(
        """
<div class="welcome-section">
    <h1 class="welcome-title">🧠 Piattaforma di Valutazione LLM</h1>
    <p class="subtitle">Una piattaforma completa per valutare le risposte LLM con diversi provider AI</p>
</div>
""",
        unsafe_allow_html=True,
    )

    # Box delle funzionalità con icone e stile migliorato
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
    <div class="feature-box">
        <p class="feature-title">
            <span class="icon-large">📋</span>
            Gestione delle Domande
        </p>
        <p class="feature-description">
            Crea, modifica e organizza le tue domande di test con le risposte previste.
            Costruisci set di test completi per valutare le risposte LLM in modo efficiente.
        </p>
    </div>

    <div class="feature-box">
        <p class="feature-title">
            <span class="icon-large">🔌</span>
            Supporto Multi-Provider API
        </p>
        <p class="feature-description">
            Connettiti a OpenAI, Anthropic o X.AI con selezione personalizzata del modello.
            Configura parametri API e verifica le connessioni con feedback in tempo reale.
        </p>
    </div>
    """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
    <div class="feature-box">
        <p class="feature-title">
            <span class="icon-large">🧪</span>
            Valutazione Automatizzata
        </p>
        <p class="feature-description">
            Esegui test con punteggio automatico rispetto alle risposte previste.
            Valuta la somiglianza semantica tra testi con modelli linguistici.
        </p>
    </div>

    <div class="feature-box">
        <p class="feature-title">
            <span class="icon-large">📊</span>
            Analisi Avanzata
        </p>
        <p class="feature-description">
            Visualizza i risultati dei test con grafici interattivi e metriche dettagliate.
            Analizza parole chiave mancanti e ottieni suggerimenti di miglioramento specifici.
        </p>
    </div>
    """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
<div class="getting-started">
    <h3>🚀 Iniziare</h3>
    <ol>
        <li>Configura le tue credenziali API nella pagina <strong>Configurazione API</strong></li>
        <li>Crea domande e risposte previste nella pagina <strong>Gestione Domande</strong></li>
        <li>Organizza le domande in set nella pagina <strong>Gestione Set di Domande</strong></li>
        <li>Esegui valutazioni nella pagina <strong>Esecuzione Test</strong></li>
        <li>Visualizza e analizza i risultati nella pagina <strong>Visualizzazione Risultati</strong></li>
    </ol>
    <p>Utilizza la barra laterale a sinistra per navigare tra queste funzionalità.</p>
</div>
""",
        unsafe_allow_html=True,
    )


if selected_page == "Home":
    show_home_page()
else:
    module_name = PAGES[selected_page]
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    else:
        importlib.import_module(module_name)
