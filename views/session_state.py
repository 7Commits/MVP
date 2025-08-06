import logging

import streamlit as st

from controllers import get_initial_state
logger = logging.getLogger(__name__)


def ensure_keys(defaults: dict) -> None:
    """Garantisce la presenza delle chiavi in ``st.session_state``.

    Parametri:
        defaults: Dizionario con chiavi e valori da impostare se mancanti.
    """
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def initialize_session_state() -> None:
    """Inizializza ``st.session_state`` con i valori di default."""
    required_keys = [
        "questions",
        "question_sets",
        "results",
        "api_key",
        "endpoint",
        "model",
        "temperature",
        "max_tokens",
    ]
    if any(key not in st.session_state for key in required_keys):
        defaults = get_initial_state()
        ensure_keys(defaults)
