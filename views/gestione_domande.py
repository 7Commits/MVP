import logging

import streamlit as st
import pandas as pd

from controllers import (
    add_question,
    update_question,
    delete_question,
    filter_questions_by_category,
    load_questions,
    import_questions_from_file,
)
from views.style_utils import add_page_header
from views.state_models import QuestionPageState
logger = logging.getLogger(__name__)


# === FUNZIONI DI CALLBACK ===


def save_question_action(
    question_id, edited_question, edited_answer, edited_category
) -> QuestionPageState:
    """Salva le modifiche alla domanda e restituisce lo stato dell'operazione."""
    state = QuestionPageState()
    if update_question(
        question_id,
        domanda=edited_question,
        risposta_attesa=edited_answer,
        categoria=edited_category,
    ):
        state.save_success = True
        st.session_state.questions = load_questions()
        state.trigger_rerun = True
    else:
        state.save_error = True
    return state


def create_save_question_callback(
    question_id, edited_question, edited_answer, edited_category
):
    def callback():
        st.session_state.question_page_state = save_question_action(
            question_id, edited_question, edited_answer, edited_category
        )

    return callback


def delete_question_action(question_id) -> QuestionPageState:
    """Elimina la domanda e restituisce lo stato dell'operazione."""
    state = QuestionPageState()
    delete_question(question_id)
    state.delete_success = True
    st.session_state.questions = load_questions()
    state.trigger_rerun = True
    return state


def import_questions_action(uploaded_file) -> QuestionPageState:
    """Importa le domande da file e restituisce lo stato dell'operazione."""
    state = QuestionPageState()
    if uploaded_file is not None:
        success, message = import_questions_from_file(uploaded_file)
        if success:
            state.import_success = True
            state.import_success_message = message
            st.session_state.questions = load_questions()
            state.trigger_rerun = True
        else:
            state.import_error = True
            state.import_error_message = message
    return state


def import_questions_callback():
    uploaded_file = st.session_state.get("uploaded_file_content")
    st.session_state.question_page_state = import_questions_action(uploaded_file)
    st.session_state.upload_questions_file = None
    st.session_state.uploaded_file_content = None


# === FUNZIONI DI DIALOGO ===

@st.dialog("Conferma Eliminazione")
def confirm_delete_question_dialog(question_id, question_text):
    """Dialogo di conferma per l'eliminazione della domanda"""
    st.write("Sei sicuro di voler eliminare questa domanda?")
    st.write(f"**Domanda:** {question_text[:100]}...")
    st.warning("Questa azione non può essere annullata.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Sì, Elimina", type="primary", use_container_width=True):
            st.session_state.question_page_state = delete_question_action(question_id)
            st.rerun()

    with col2:
        if st.button("No, Annulla", use_container_width=True):
            st.rerun()


def render():
    # === Inizializzazione dello stato ===
    st.session_state.setdefault("question_page_state", QuestionPageState())
    state: QuestionPageState = st.session_state.question_page_state

    # Carica le domande utilizzando la cache
    st.session_state.questions = load_questions()

    # Gestisce la logica di rerun
    if state.trigger_rerun:
        state.trigger_rerun = False
        st.rerun()

    # Mostra i messaggi di stato
    if state.save_success:
        st.success(state.save_success_message)
    if state.save_error:
        st.error(state.save_error_message)
    if state.delete_success:
        st.success(state.delete_success_message)
    if state.add_success:
        st.success(state.add_success_message)
    if state.import_success:
        st.success(state.import_success_message)
    if state.import_error:
        st.error(state.import_error_message)

    # Resetta lo stato dopo la visualizzazione dei messaggi
    st.session_state.question_page_state = QuestionPageState()

    # Aggiungi un'intestazione stilizzata
    add_page_header(
        "Gestione Domande",
        icon="📋",
        description="Crea, modifica e gestisci le tue domande, le risposte attese e le categorie."
    )

    # Scheda per diverse funzioni di gestione delle domande
    tabs = st.tabs(["Visualizza & Modifica Domande", "Aggiungi Domande", "Importa da File"])

    # Scheda Visualizza e Modifica Domande
    with tabs[0]:
        st.header("Visualizza e Modifica Domande")

        if 'questions' in st.session_state and not st.session_state.questions.empty:
            questions_df, unique_categories = filter_questions_by_category()
            category_options = ["Tutte le categorie"] + unique_categories

            selected_category = st.selectbox(
                "Filtra per categoria:",
                options=category_options,
                index=0
            )

            if selected_category == "Tutte le categorie":
                filtered_questions_df = questions_df
            else:
                filtered_questions_df, _ = filter_questions_by_category(selected_category)

            if not filtered_questions_df.empty:
                for idx, row in filtered_questions_df.iterrows():
                    category_display = row.get('categoria', 'N/A') if pd.notna(row.get('categoria')) else 'N/A'
                    with st.expander(
                        f"Domanda: {row['domanda'][:100]}... (Categoria: {category_display})"
                    ):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            edited_question = st.text_area(
                                f"Modifica Domanda {idx + 1}",
                                value=row['domanda'],
                                key=f"q_edit_{row['id']}"
                            )

                            edited_answer = st.text_area(
                                f"Modifica Risposta Attesa {idx + 1}",
                                value=row['risposta_attesa'],
                                key=f"a_edit_{row['id']}"
                            )

                            edited_category_value = row.get('categoria', '')
                            edited_category = st.text_input(
                                f"Modifica Categoria {idx + 1}",
                                value=edited_category_value,
                                key=f"c_edit_{row['id']}"
                            )

                        with col2:
                            st.button(
                                "Salva Modifiche",
                                key=f"save_{row['id']}",
                                on_click=create_save_question_callback(
                                    row['id'], edited_question, edited_answer, edited_category
                                ),
                            )

                            if st.button(
                                    "Elimina Domanda",
                                    key=f"delete_{row['id']}",
                                    type="secondary"
                            ):
                                confirm_delete_question_dialog(row['id'], row['domanda'])
            else:
                st.info(f"Nessuna domanda trovata per la categoria '{selected_category}'.")

        else:
            st.info("Nessuna domanda disponibile. Aggiungi domande utilizzando la scheda 'Aggiungi Domande'.")

    # Scheda Aggiungi Domande
    with tabs[1]:
        st.header("Aggiungi Nuova Domanda")

        with st.form("add_question_form"):
            domanda = st.text_area("Domanda", placeholder="Inserisci qui la domanda...")
            risposta_attesa = st.text_area("Risposta Attesa", placeholder="Inserisci qui la risposta attesa...")
            categoria = st.text_input("Categoria (opzionale)", placeholder="Inserisci qui la categoria...")

            submitted = st.form_submit_button("Aggiungi Domanda")

            if submitted:
                if domanda and risposta_attesa:
                    # Passa la categoria, che può essere una stringa vuota se non inserita
                    question_id = add_question(
                        domanda=domanda,
                        risposta_attesa=risposta_attesa,
                        categoria=categoria,
                    )
                    state = QuestionPageState()
                    state.add_success = True
                    state.add_success_message = (
                        f"Domanda aggiunta con successo con ID: {question_id}"
                    )
                    state.trigger_rerun = True
                    st.session_state.question_page_state = state
                    st.session_state.questions = load_questions()
                    st.rerun()
                else:
                    st.error("Sono necessarie sia la domanda che la risposta attesa.")

    # Scheda Importa da File
    with tabs[2]:
        st.header("Importa Domande da File")

        st.write("""
        Carica un file CSV o JSON contenente domande, risposte attese e categorie (opzionale).

        ### Formato File:
        - **CSV**: Deve includere le colonne 'domanda' e 'risposta_attesa'.
          Può includere opzionalmente 'categoria'.
          (Se usi i vecchi nomi 'question' e 'expected_answer', verranno convertiti automaticamente).
        - **JSON**: Deve contenere un array di oggetti con i campi 'domanda' e 'risposta_attesa'.
          Può includere opzionalmente 'categoria'.
          (Se usi i vecchi nomi 'question' e 'expected_answer', verranno convertiti automaticamente).

        ### Esempio CSV:
        ```csv
        domanda,risposta_attesa,categoria
        "Quanto fa 2+2?","4","Matematica Base"
        "Qual è la capitale della Francia?","Parigi","Geografia"
        "Chi ha scritto 'Amleto'?","William Shakespeare","Letteratura"
        ```

        ### Esempio JSON:
        ```json
        [
            {
                "domanda": "Quanto fa 2+2?",
                "risposta_attesa": "4",
                "categoria": "Matematica Base"
            },
            {
                "domanda": "Qual è la capitale della Francia?",
                "risposta_attesa": "Parigi",
                "categoria": "Geografia"
            },
            {
                "domanda": "Chi ha scritto 'Romeo e Giulietta'?",
                "risposta_attesa": "William Shakespeare"
            }
        ]
        ```
        """)

        uploaded_file = st.file_uploader(
            "Scegli un file", type=["csv", "json"], key="upload_questions_file"
        )

        if uploaded_file is not None:
            # Salva il file in session_state per l'uso da parte della callback
            st.session_state.uploaded_file_content = uploaded_file

            # Pulsante che utilizza la funzione di callback
            st.button(
                "Importa Domande",
                key="import_questions_btn",
                on_click=import_questions_callback
            )
