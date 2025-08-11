import logging

import streamlit as st
import pandas as pd

from controllers import (
    add_question,
    get_filtered_questions,
    load_questions,
    save_question_action,
    delete_question_action,
    import_questions_action,
)
from views.style_utils import add_page_header
from views.state_models import QuestionPageState
logger = logging.getLogger(__name__)


# === FUNZIONI DI CALLBACK ===


def create_save_question_callback(
    question_id, edited_question, edited_answer, edited_category
):
    def callback():
        state = QuestionPageState()
        try:
            result = save_question_action(
                question_id, edited_question, edited_answer, edited_category
            )
            if result["success"]:
                state.save_success = True
                state.save_success_message = "Domanda salvata."
                st.session_state.questions = result["questions_df"]
                state.trigger_rerun = True
            else:
                state.save_error = True
                state.save_error_message = "Domanda non salvata."
        except Exception as e:
            state.save_error = True
            state.save_error_message = f"Domanda non salvata: {e}"
        st.session_state.question_page_state = state

    return callback


def import_questions_callback():
    uploaded_file = st.session_state.get("uploaded_file_content")
    state = QuestionPageState()
    try:
        result = import_questions_action(uploaded_file)
        st.session_state.questions = result["questions_df"]
        count = result.get("imported_count", 0)
        warnings = result.get("warnings", [])

        if count > 0:
            state.import_success = True
            msg = f"Importate con successo {count} domande."
            if warnings:
                msg = f"{msg} Avvisi: {'; '.join(warnings)}"
            state.import_success_message = msg
        else:
            state.import_error = True
            msg = "Nessuna domanda importata."
            if warnings:
                msg = f"{msg} {'; '.join(warnings)}"
            state.import_error_message = msg

        state.trigger_rerun = True
    except Exception as e:
        state.import_error = True
        state.import_error_message = str(e)
    st.session_state.question_page_state = state
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
            state = QuestionPageState()
            try:
                questions = delete_question_action(question_id)
                state.delete_success = True
                st.session_state.questions = questions
                state.trigger_rerun = True
            except Exception as e:
                state.save_error = True
                state.save_error_message = str(e)
            st.session_state.question_page_state = state
            st.rerun()

    with col2:
        if st.button("No, Annulla", use_container_width=True):
            st.rerun()


def render():
    # === Inizializzazione dello stato ===
    st.session_state.setdefault("question_page_state", QuestionPageState())
    state: QuestionPageState = st.session_state.question_page_state

    # Carica le domande utilizzando la cache solo se non già presenti
    if "questions" not in st.session_state:
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
            _, categories = get_filtered_questions()
            category_options = ["Tutte le categorie"] + categories

            selected_category = st.selectbox(
                "Filtra per categoria:",
                options=category_options,
                index=0
            )

            filter_cat = None if selected_category == "Tutte le categorie" else selected_category
            filtered_questions_df, _ = get_filtered_questions(filter_cat)

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
