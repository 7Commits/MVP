"""Funzioni di utilità per applicare stili CSS nelle viste Streamlit.

Centralizza l'iniezione di CSS per favorirne il riuso tra le pagine.
"""

import logging
import streamlit as st
from pathlib import Path

logger = logging.getLogger(__name__)


def load_css():
    """
    Applica il CSS globale presente in 'styles.css'.
    """
    css_path = Path(__file__).parent.parent / "views" / "styles.css"
    if css_path.exists():
        css_content = css_path.read_text()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.warning("File styles.css non trovato. Assicurati che sia presente nella cartella views.")


def add_global_styles():
    """Aggiunge stili globali all'applicazione."""
    load_css()


def add_page_header(title: str, icon: str = "💡", description: str | None = None):
    """Aggiunge un'intestazione di pagina stilizzata."""
    load_css()
    st.markdown(
        f"""
    <div class="page-header">
        <div class="page-title">{icon} {title}</div>
        {f'<div class="page-description">{description}</div>' if description else ''}
    </div>
    <hr class="header-divider">
    """,
        unsafe_allow_html=True,
    )


def add_section_title(title: str, icon: str | None = None):
    """Aggiunge un titolo di sezione stilizzato."""
    icon_text = f"{icon} " if icon else ""
    st.markdown(
        f"<div class=\"section-title\">{icon_text}{title}</div>",
        unsafe_allow_html=True,
    )


def add_home_styles():
    """Applica gli stili CSS specifici della home page.

    Migliora la visibilità degli input nei temi chiaro e scuro e definisce
    l'aspetto degli elementi principali come box funzionali e sezioni di
    benvenuto.
    """
    load_css()
