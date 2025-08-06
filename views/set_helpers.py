import logging

import streamlit as st

from controllers import (
    update_set,
    delete_set,
    refresh_question_sets,
    import_sets_from_file,
    refresh_questions,
)
from .state_models import SetPageState
logger = logging.getLogger(__name__)


def save_set_callback(
    set_id: str,
    edited_name: str,
    question_options_checkboxes: dict,
    newly_selected_questions_ids: list[str],
    state: SetPageState,
) -> None:
    kept_questions_ids = [q_id for q_id, keep in question_options_checkboxes.items() if keep]
    updated_questions_ids = list(
        set(kept_questions_ids + [str(q_id) for q_id in newly_selected_questions_ids])
    )

    update_set(set_id, edited_name, updated_questions_ids)
    state.save_set_success_message = "Set di domande aggiornato con successo!"
    state.save_set_success = True
    st.session_state.question_sets = refresh_question_sets()
    state.trigger_rerun = True


def delete_set_callback(set_id: str, state: SetPageState):
    delete_set(set_id)
    state.delete_set_success_message = "Set di domande eliminato con successo!"
    state.delete_set_success = True
    st.session_state.question_sets = refresh_question_sets()
    state.trigger_rerun = True


@st.dialog("Conferma Eliminazione")
def confirm_delete_set_dialog(set_id: str, set_name: str, state: SetPageState):
    """Dialog di conferma per l'eliminazione del set di domande"""
    st.write(f"Sei sicuro di voler eliminare il set '{set_name}'?")
    st.warning("Questa azione non può essere annullata.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Sì, Elimina", type="primary", use_container_width=True):
            delete_set_callback(set_id, state)
            st.rerun()

    with col2:
        if st.button("No, Annulla", use_container_width=True):
            st.rerun()


def import_set_callback(state: SetPageState):
    """Importa uno o più set di domande da file JSON o CSV."""

    state.import_set_success = False
    state.import_set_error = False
    state.import_set_success_message = ""
    state.import_set_error_message = ""

    uploaded_file = st.session_state.get("uploaded_file_content_set")
    result = import_sets_from_file(uploaded_file)

    if result["success"]:
        state.import_set_success = True
        state.import_set_success_message = result["success_message"]
        st.session_state.questions = refresh_questions()
        st.session_state.question_sets = refresh_question_sets()
    else:
        state.import_set_error = True
        state.import_set_error_message = result["error_message"]

    for warn in result.get("warnings", []):
        st.warning(warn)

    st.session_state.uploaded_file_content_set = None
    st.session_state.pop("upload_set_file", None)
    state.trigger_rerun = True


def get_question_text(question_id: str) -> str:
    """Ritorna il testo della domanda dato il suo ID."""
    if "questions" in st.session_state and not st.session_state.questions.empty:
        if "domanda" not in st.session_state.questions.columns:
            st.session_state.questions = refresh_questions()
            if "domanda" not in st.session_state.questions.columns:
                return f"ID Domanda: {question_id} (colonna 'domanda' mancante)"

        question_row = st.session_state.questions[st.session_state.questions["id"] == str(question_id)]
        if not question_row.empty:
            return question_row.iloc[0]["domanda"]
    return f"ID Domanda: {question_id} (non trovata o dati non caricati)"


def get_question_category(question_id: str, questions_df):
    """Ritorna la categoria di una domanda dato il suo ID."""
    if questions_df is not None and not questions_df.empty and "categoria" in questions_df.columns:
        question_row = questions_df[questions_df["id"] == str(question_id)]
        if not question_row.empty:
            return question_row.iloc[0]["categoria"]
    return "N/A"


def mark_expander_open(exp_key: str):
    """Segna l'expander come aperto nello stato di sessione"""
    if "set_expanders" in st.session_state:
        st.session_state.set_expanders[exp_key] = True


def create_save_set_callback(set_id: str, exp_key: str, state: SetPageState):
    def callback():
        mark_expander_open(exp_key)
        edited_name = st.session_state.get(f"set_name_{set_id}", "")
        question_options_checkboxes = st.session_state.question_checkboxes.get(set_id, {})
        newly_selected_questions_ids = st.session_state.newly_selected_questions.get(set_id, [])

        save_set_callback(
            set_id,
            edited_name,
            question_options_checkboxes,
            newly_selected_questions_ids,
            state,
        )

    return callback


def create_delete_set_callback(set_id: str, state: SetPageState):
    def callback():
        delete_set_callback(set_id, state)

    return callback
