import logging

import streamlit as st

from views import (
    api_configurazione,
    esecuzione_test,
    gestione_domande,
    gestione_set,
    home,
    visualizza_risultati,
)
from views.session_state import initialize_session_state
from views.style_utils import add_global_styles
from controllers.startup_controller import setup_logging

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
add_global_styles()

PAGES = {
    "Home": home.render,
    "Configurazione API": api_configurazione.render,
    "Gestione Domande": gestione_domande.render,
    "Gestione Set di Domande": gestione_set.render,
    "Esecuzione Test": esecuzione_test.render,
    "Visualizzazione Risultati": visualizza_risultati.render,
}

selected_page = st.sidebar.radio("Navigazione", list(PAGES.keys()))

render_page = PAGES[selected_page]
render_page()
