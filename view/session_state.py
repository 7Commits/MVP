import streamlit as st


def ensure_keys(defaults: dict) -> None:
    """Garantisce la presenza delle chiavi in ``st.session_state``.

    Args:
        defaults: Dizionario con chiavi e valori da impostare se mancanti.
    """
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

