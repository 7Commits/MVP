"""Modulo della vista per la pagina Home dell'applicazione Streamlit."""

import logging

import streamlit as st
from views.style_utils import add_home_styles
from views import register_page

logger = logging.getLogger(__name__)


#@register_page("Home")
def render():
    """Visualizza la pagina principale con le funzionalità della piattaforma."""

    add_home_styles()

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

if __name__ == "__main__":
    render()
else:
    render()
