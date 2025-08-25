import logging

import streamlit as st

from views.session_state import initialize_session_state
from views.style_utils import load_css
from utils.startup_utils import setup_logging

logger = logging.getLogger(__name__)

setup_logging()
logger.info("Applicazione avviata")

# Imposta la configurazione della pagina
st.set_page_config(
    page_title="LLM Test Evaluation Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
initialize_session_state()

# Applicazione principale
st.title("🧠 LLM Test Evaluation Platform - Artificial QI")

# Aggiungi CSS personalizzato e stili globali
load_css()

# --- Definizione pagine con il nuovo sistema ---
Home = st.Page("views/home.py", title="Home", icon=":material/home:", default=True)
Configurazione_API = st.Page("views/api_configurazione.py", title="Configurazione API", icon=":material/api:")
Gestione_domande = st.Page("views/gestione_domande.py", title="Gestione Domande", icon=":material/construction:")
Gestione_set = st.Page("views/gestione_set.py", title="Gestione Set di Domande", icon=":material/list:")
Esecuzione_test = st.Page("views/esecuzione_test.py", title="Esecuzione Test", icon=":material/rule_settings:")
Visualizza_risultati = st.Page("views/visualizza_risultati.py",
                               title="Visualizzazione Risultati",
                               icon=":material/bar_chart:")

# --- Navigazione ---
pg = st.navigation([Home, Configurazione_API, Gestione_domande, Gestione_set, Esecuzione_test, Visualizza_risultati])
pg.run()
