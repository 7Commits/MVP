import logging

import streamlit as st

from controllers import update_set, delete_set
from models.question_set import QuestionSet
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

    try:
        result = update_set(set_id, edited_name, updated_questions_ids)
        if isinstance(result, tuple):
            sets_df = result[0]
            message = result[1] if len(result) > 1 else "Set di domande aggiornato con successo!"
            if len(result) > 2 and isinstance(result[2], list):
                for warn in result[2]:
                    st.warning(warn)
        else:
            sets_df = result
            message = "Set di domande aggiornato con successo!"

        state.save_set_success_message = message
        state.save_set_success = True
        if sets_df is not None:
            st.session_state.question_sets = sets_df
    except Exception as exc:  # pragma: no cover - UI error handling
        state.save_set_error = True
        state.save_set_error_message = str(exc)

    state.trigger_rerun = True


def delete_set_callback(set_id: str, state: SetPageState):
    try:
        result = delete_set(set_id)
        if isinstance(result, tuple):
            sets_df = result[0]
            message = result[1] if len(result) > 1 else "Set di domande eliminato con successo!"
            if len(result) > 2 and isinstance(result[2], list):
                for warn in result[2]:
                    st.warning(warn)
        else:
            sets_df = result
            message = "Set di domande eliminato con successo!"

        state.delete_set_success_message = message
        state.delete_set_success = True
        if sets_df is not None:
            st.session_state.question_sets = sets_df
    except Exception as exc:  # pragma: no cover - UI error handling
        state.save_set_error = True
        state.save_set_error_message = str(exc)

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
    try:
        result = QuestionSet.import_from_file(uploaded_file)

        parts: list[str] = []
        if result.sets_imported_count > 0:
            parts.append(f"{result.sets_imported_count} set importati")
        if result.new_questions_added_count > 0:
            parts.append(f"{result.new_questions_added_count} nuove domande aggiunte")
        if result.existing_questions_found_count > 0:
            parts.append(
                f"{result.existing_questions_found_count} domande esistenti referenziate"
            )

        if parts:
            message = ". ".join(parts) + "."
        else:
            message = "Nessun set importato."
            if result.warnings:
                message += " Controlla gli avvisi."

        state.import_set_success = True
        state.import_set_success_message = message

        if result.questions_df is not None:
            st.session_state.questions = result.questions_df
        if result.sets_df is not None:
            st.session_state.question_sets = result.sets_df
        for warn in result.warnings:
            st.warning(warn)
    except Exception as exc:  # pragma: no cover - UI error handling
        state.import_set_error = True
        state.import_set_error_message = str(exc)

    st.session_state.uploaded_file_content_set = None
    st.session_state.pop("upload_set_file", None)
    state.trigger_rerun = True


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
