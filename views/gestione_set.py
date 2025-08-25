import logging
import streamlit as st
from controllers import (
    create_set,
    load_sets,
    prepare_sets_for_view,
)
# from views import register_page
from views.style_utils import add_page_header, add_global_styles
from views.state_models import SetPageState
from views.set_helpers import (
    confirm_delete_set_dialog,
    import_set_callback,
    mark_expander_open,
    create_save_set_callback,
)

logger = logging.getLogger(__name__)


# @register_page("Gestione Set di Domande")
def render():
    add_global_styles()

    st.session_state.setdefault("set_page_state", SetPageState())
    state: SetPageState = st.session_state.set_page_state

    st.session_state.setdefault("question_checkboxes", {})
    st.session_state.setdefault("newly_selected_questions", {})
    st.session_state.setdefault("set_expanders", {})

    if state.trigger_rerun:
        state.trigger_rerun = False
        st.rerun()

    if state.save_set_success:
        st.success(state.save_set_success_message)
        state.save_set_success = False

    if state.save_set_error:
        st.error(state.save_set_error_message)
        state.save_set_error = False

    if state.delete_set_success:
        st.success(state.delete_set_success_message)
        state.delete_set_success = False

    if state.create_set_success:
        st.success(state.create_set_success_message)
        state.create_set_success = False

    if state.import_set_success:
        st.success(state.import_set_success_message)
        state.import_set_success = False

    if state.import_set_error:
        st.error(state.import_set_error_message)
        state.import_set_error = False

    # Inizializza i dati tramite il controller
    initial_data = prepare_sets_for_view()
    st.session_state.questions = initial_data["questions_df"]
    st.session_state.question_sets = initial_data["raw_sets_df"]

    # Assicurati che esista lo stato degli expander per ogni set
    if 'question_sets' in st.session_state and not st.session_state.question_sets.empty:
        current_set_ids = st.session_state.question_sets['id'].tolist()
        # Rimuovi stati per set non più presenti
        for sid in list(st.session_state.set_expanders.keys()):
            if sid not in current_set_ids:
                del st.session_state.set_expanders[sid]
        # Aggiungi stato predefinito per nuovi set
        for sid in current_set_ids:
            st.session_state.set_expanders.setdefault(sid, False)

    # Aggiungi un'intestazione stilizzata
    add_page_header(
        "Gestione Set di Domande",
        icon="📚",
        description="Organizza le tue domande in set per test e valutazioni"
    )

    # Schede per diverse funzioni di gestione dei set
    tabs = st.tabs(["Visualizza & Modifica Set", "Crea Nuovo Set", "Importa Set da file"])

    # Scheda Visualizza e Modifica Set
    with tabs[0]:
        st.header("Visualizza e Modifica Set di Domande")

        categories = initial_data["categories"]
        selected_categories = st.multiselect(
            "Filtra per categorie (mostra i set che contengono almeno una domanda da OGNI categoria selezionata):",
            options=categories,
            default=[],
            key="filter_categories",
        )

        data = prepare_sets_for_view(selected_categories)
        questions_df = data["questions_df"]
        display_sets_df = data["sets_df"]
        st.session_state.questions = questions_df

        questions_ready = (
            not questions_df.empty
            and 'domanda' in questions_df.columns
            and 'categoria' in questions_df.columns
        )

        if display_sets_df.empty:
            if selected_categories:
                st.info(
                    "Nessun set trovato che contenga domande da tutte le categorie selezionate: "
                    f"{', '.join(selected_categories)}."
                )
            else:
                st.info(
                    "Nessun set di domande disponibile. Crea un nuovo set utilizzando la scheda 'Crea Nuovo Set'."
                )
        else:
            for idx, row in display_sets_df.iterrows():
                exp_key = f"set_expander_{row['id']}"
                if exp_key not in st.session_state.set_expanders:
                    st.session_state.set_expanders[exp_key] = False

                with st.expander(
                    f"{row['name']}",
                    expanded=st.session_state.set_expanders.get(exp_key, False),
                ):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        _ = st.text_input(
                            "Nome Set",
                            value=row['name'],
                            key=f"set_name_{row['id']}",
                            on_change=mark_expander_open,
                            args=(exp_key,)
                        )

                        st.subheader("Domande in questo Set")
                        current_question_ids_in_set = row.get('questions', [])
                        if not isinstance(current_question_ids_in_set, list):
                            current_question_ids_in_set = []

                        if row['id'] not in st.session_state.question_checkboxes:
                            st.session_state.question_checkboxes[row['id']] = {}

                        questions_detail = row.get('questions_detail', [])
                        if questions_detail:
                            for q in questions_detail:
                                q_id = str(q.get('id'))
                                q_text = q.get('domanda', f"ID Domanda: {q_id} (non trovata)")
                                q_cat = q.get('categoria', 'N/A')
                                display_text = f"{q_text} (Categoria: {q_cat})"

                                checkbox_value = st.checkbox(
                                    display_text,
                                    value=True,
                                    key=f"qcheck_{row['id']}_{q_id}",
                                    on_change=mark_expander_open,
                                    args=(exp_key,),
                                )
                                st.session_state.question_checkboxes[row['id']][q_id] = checkbox_value
                        else:
                            st.info("Nessuna domanda in questo set.")
                        st.subheader("Aggiungi Domande al Set")

                        # 初始化新选择的问题状态
                        if row['id'] not in st.session_state.newly_selected_questions:
                            st.session_state.newly_selected_questions[row['id']] = []

                        if questions_ready:
                            all_questions_df = st.session_state.questions
                            available_questions_df = all_questions_df[
                                ~all_questions_df['id'].astype(str).isin(
                                    [str(q_id) for q_id in current_question_ids_in_set]
                                )
                            ]

                            if not available_questions_df.empty:
                                question_dict_for_multiselect = {
                                    q_id: f"{q_text} (Cat: {q_cat})"
                                    for q_id, q_text, q_cat in zip(
                                        available_questions_df['id'].astype(str),
                                        available_questions_df['domanda'],
                                        available_questions_df['categoria'],
                                    )
                                }
                                newly_selected_questions_ids = st.multiselect(
                                    "Seleziona domande da aggiungere",
                                    options=list(question_dict_for_multiselect.keys()),
                                    format_func=lambda x: question_dict_for_multiselect.get(x, x),
                                    key=f"add_q_{row['id']}",
                                    on_change=mark_expander_open,
                                    args=(exp_key,)
                                )
                                st.session_state.newly_selected_questions[row['id']] = newly_selected_questions_ids
                            else:
                                st.info("Nessuna altra domanda disponibile da aggiungere.")
                        else:
                            st.info("Le domande non sono disponibili per la selezione (dati mancanti o incompleti).")

                    with col2:
                        st.button(
                            "Salva Modifiche",
                            key=f"save_set_{row['id']}",
                            on_click=create_save_set_callback(row['id'], exp_key, state)
                        )

                        # Pulsante Elimina con dialog di conferma
                        if st.button(
                            "Elimina Set",
                            key=f"delete_set_{row['id']}",
                            type="secondary"
                        ):
                            mark_expander_open(exp_key)
                            confirm_delete_set_dialog(row['id'], row['name'], state)

                # Lo stato dell'expander viene aggiornato tramite i callback

    # Scheda Crea Nuovo Set
    with tabs[1]:
        st.header("Crea Nuovo Set di Domande")

        with st.form("create_set_form"):
            set_name = st.text_input("Nome Set", placeholder="Inserisci un nome per il set...")

            selected_qs_for_new_set = []
            questions_ready_for_creation = (
                'questions' in st.session_state and
                not st.session_state.questions.empty and
                'domanda' in st.session_state.questions.columns and
                'categoria' in st.session_state.questions.columns
            )

            if questions_ready_for_creation:
                all_questions_df_creation = st.session_state.questions
                question_dict_for_creation = {
                    q_id: f"{q_text} (Cat: {q_cat})"
                    for q_id, q_text, q_cat in zip(
                        all_questions_df_creation['id'].astype(str),
                        all_questions_df_creation['domanda'],
                        all_questions_df_creation['categoria'],
                    )
                }

                selected_qs_for_new_set = st.multiselect(
                    "Seleziona domande per questo set",
                    options=list(question_dict_for_creation.keys()),
                    format_func=lambda x: question_dict_for_creation.get(x, x),
                    key="create_set_questions",
                )
            else:
                st.info(
                    "Nessuna domanda disponibile o dati delle domande non pronti (incl. categorie). \n"
                    "Vai a 'Gestione Domande' per aggiungere/caricare domande."
                )

            submitted = st.form_submit_button("Crea Set")

            if submitted:
                if set_name:
                    set_id = create_set(
                        set_name, [str(q_id) for q_id in selected_qs_for_new_set]
                    )
                    st.session_state.question_sets = load_sets()
                    state.create_set_success_message = (
                        f"Set di domande creato con successo con ID: {set_id}"
                    )
                    state.create_set_success = True
                    state.trigger_rerun = True
                    st.rerun()
                else:
                    st.error("Il nome del set è obbligatorio.")

    # Scheda Importa da File
    with tabs[2]:
        st.header("Importa Set da File")

        st.write("""
        Carica un file JSON o CSV contenente uno o più set di domande.

        ### Formato File JSON per Set Multipli:
        ```json
        [
            {
                "name": "Capitali",
                "questions": [
                    {
                        "id": "1",
                        "domanda": "Qual è la capitale della Francia?",
                        "risposta_attesa": "Parigi",
                        "categoria": "Geografia"
                    },
                    {
                        "id": "2",
                        "domanda": "Qual è la capitale della Germania?",
                        "risposta_attesa": "Berlino",
                        "categoria": "Geografia"
                    }
                ]
            },
            {
                "name": "Matematica Base",
                "questions": [
                    {
                        "id": "3",
                        "domanda": "Quanto fa 2+2?",
                        "risposta_attesa": "4",
                        "categoria": "Matematica"
                    },
                    {
                        "id": "4",
                        "domanda": "Quanto fa 10*4?",
                        "risposta_attesa": "40",
                        "categoria": "Matematica"
                    }
                ]
            }
        ]
        ```

        ### Formato CSV:
        Ogni riga deve contenere le colonne ``name`` (nome del set), ``id``
        (ID della domanda), ``domanda`` (testo), ``risposta_attesa`` e
        ``categoria``.
        ```csv
        name,id,domanda,risposta_attesa,categoria
        Capitali,1,Qual è la capitale della Francia?,Parigi,Geografia
        Capitali,2,Qual è la capitale della Germania?,Berlino,Geografia
        Matematica Base,3,Quanto fa 2+2?,4,Matematica
        Matematica Base,4,Quanto fa 10*4?,40,Matematica
        ```

        ### Note Importanti:
        - Se una domanda con lo stesso ID esiste già, non verrà aggiunta nuovamente
        - Se un set con lo stesso nome esiste già, verrà saltato
        - Solo le domande nuove verranno aggiunte al database
        - Le domande esistenti verranno referenziate nei nuovi set
        """)

        uploaded_file = st.file_uploader(
            "Scegli un file", type=["json", "csv"], key="upload_set_file"
        )

        if uploaded_file is not None:
            st.session_state.uploaded_file_content_set = uploaded_file
            st.button(
                "Importa Set",
                key="import_set_btn",
                on_click=lambda: import_set_callback(state)
            )


if __name__ == "__main__":
    render()
else:
    render()
