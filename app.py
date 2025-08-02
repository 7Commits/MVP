import logging

import streamlit as st

from view import (
    api_configurazione,
    esecuzione_test,
    gestione_domande,
    gestione_set,
    home,
    visualizza_risultati,
)
from view.session_state import initialize_session_state
from view.style_utils import add_global_styles
from logging_config import setup_logging

setup_logging()
logging.info("Applicazione avviata")

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
