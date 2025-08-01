import streamlit as st
from controllers.question_set_controller import (
    load_sets,
    create_set,
)
from controllers.question_controller import load_questions
from view.style_utils import add_page_header, add_section_title
from view.component_utils import create_card, create_metrics_container
from view.session_state import ensure_keys
from view.set_helpers import (
    save_set_callback,
    delete_set_callback,
    confirm_delete_set_dialog,
    import_set_callback,
    get_question_text,
    get_question_category,
    mark_expander_open,
    create_save_set_callback,
    create_delete_set_callback,
)


ensure_keys({
    "save_set_success": False,
    "save_set_error": False,
    "delete_set_success": False,
    "create_set_success": False,
    "import_set_success": False,
    "import_set_error": False,
    "trigger_rerun": False,
    "question_checkboxes": {},
    "newly_selected_questions": {},
    "set_expanders": {},
})

if st.session_state.trigger_rerun:
    st.session_state.trigger_rerun = False
    st.rerun()

if st.session_state.save_set_success:
    st.success(st.session_state.get('save_set_success_message', 'Set aggiornato con successo!'))
    st.session_state.save_set_success = False

if st.session_state.save_set_error:
    st.error(st.session_state.get('save_set_error_message', 'Errore durante l\'aggiornamento del set.'))
    st.session_state.save_set_error = False

if st.session_state.delete_set_success:
    st.success(st.session_state.get('delete_set_success_message', 'Set eliminato con successo!'))
    st.session_state.delete_set_success = False

if st.session_state.create_set_success:
    st.success(st.session_state.get('create_set_success_message', 'Set creato con successo!'))
    st.session_state.create_set_success = False

if st.session_state.import_set_success:
    st.success(st.session_state.get('import_set_success_message', 'Importazione completata con successo!'))
    st.session_state.import_set_success = False

if st.session_state.import_set_error:
    st.error(st.session_state.get('import_set_error_message', 'Errore durante l\'importazione.'))
    st.session_state.import_set_error = False

# Inizializza sempre i dati caricandoli dal database
st.session_state.questions = load_questions()
st.session_state.question_sets = load_sets()

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

# Assicurati che la colonna 'categoria' esista in questions_df e gestisci i NaN
if 'questions' in st.session_state and not st.session_state.questions.empty:
    questions_df_temp = st.session_state.questions
    if 'categoria' not in questions_df_temp.columns:
        questions_df_temp['categoria'] = 'N/A'  # Aggiungi colonna se mancante
    questions_df_temp['categoria'] = questions_df_temp['categoria'].fillna('N/A')  # Riempi NaN
    st.session_state.questions = questions_df_temp

# Aggiungi un'intestazione stilizzata
add_page_header(
    "Gestione Set di Domande",
    icon="📚",
    description="Organizza le tue domande in set per test e valutazioni"
)

# Schede per diverse funzioni di gestione dei set
tabs = st.tabs(["Visualizza & Modifica Set", "Crea Nuovo Set", "Importa Set da file"])


# Funzione per ottenere il testo della domanda tramite ID

# Scheda Visualizza e Modifica Set
with tabs[0]:
    st.header("Visualizza e Modifica Set di Domande")

    questions_ready = ('questions' in st.session_state and
                       not st.session_state.questions.empty and
                       'domanda' in st.session_state.questions.columns and
                       'categoria' in st.session_state.questions.columns)
    sets_ready = 'question_sets' in st.session_state

    if not questions_ready:
        st.warning(
            "Dati delle domande (incluse categorie) non completamente caricati. Alcune funzionalità potrebbero essere limitate. Vai a 'Gestione Domande'.")
        # Impedisci l'esecuzione del filtro se i dati delle domande non sono pronti
        unique_categories_for_filter = []
        selected_categories = []
    else:
        questions_df = st.session_state.questions
        # Ottieni categorie uniche per il filtro, escludendo 'N/A' se si preferisce non mostrarlo come opzione selezionabile
        # o gestendolo specificamente. Per ora, includiamo tutto.
        unique_categories_for_filter = sorted(list(questions_df['categoria'].astype(str).unique()))
        if not unique_categories_for_filter:
            st.info("Nessuna categoria definita nelle domande esistenti per poter filtrare.")

        selected_categories = st.multiselect(
            "Filtra per categorie (mostra i set che contengono almeno una domanda da OGNI categoria selezionata):",
            options=unique_categories_for_filter,
            default=[],
            key="filter_categories",
        )

    if sets_ready and not st.session_state.question_sets.empty:
        question_sets_df = st.session_state.question_sets
        display_sets_df = question_sets_df.copy()  # Inizia con tutti i set

        if selected_categories and questions_ready:  # Applica il filtro solo se categorie selezionate e dati pronti
            filtered_set_indices = []
            for idx, set_row in question_sets_df.iterrows():
                question_ids_in_set = set_row.get('questions', [])
                if not isinstance(question_ids_in_set, list):
                    question_ids_in_set = []

                if not question_ids_in_set:  # Se il set non ha domande, non può soddisfare il filtro
                    continue

                categories_present_in_set = set()
                for q_id in question_ids_in_set:
                    category = get_question_category(str(q_id), questions_df)
                    categories_present_in_set.add(category)

                # Verifica se il set contiene almeno una domanda da OGNI categoria selezionata
                if all(sel_cat in categories_present_in_set for sel_cat in selected_categories):
                    filtered_set_indices.append(idx)

            display_sets_df = question_sets_df.loc[filtered_set_indices]

        if display_sets_df.empty and selected_categories:
            st.info(
                f"Nessun set trovato che contenga domande da tutte le categorie selezionate: {', '.join(selected_categories)}.")
        elif display_sets_df.empty and not selected_categories:
            st.info("Nessun set di domande disponibile. Crea un nuovo set utilizzando la scheda 'Crea Nuovo Set'.")

        for idx, row in display_sets_df.iterrows():
            exp_key = f"set_expander_{row['id']}"
            if exp_key not in st.session_state.set_expanders:
                st.session_state.set_expanders[exp_key] = False

            with st.expander(
                f"Set: {row['name']}",
                expanded=st.session_state.set_expanders.get(exp_key, False),
            ):
                col1, col2 = st.columns([3, 1])

                with col1:
                    edited_name = st.text_input(
                        f"Nome Set",
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

                    if current_question_ids_in_set:
                        for q_id in current_question_ids_in_set:
                            q_text = get_question_text(str(q_id))
                            q_cat = get_question_category(str(q_id), questions_df) if questions_ready else 'N/A'
                            display_text = f"{q_text} (Categoria: {q_cat})"
                            
                            # 使用回调来更新checkbox状态
                            checkbox_value = st.checkbox(
                                display_text,
                                value=True,
                                key=f"qcheck_{row['id']}_{q_id}",
                                on_change=mark_expander_open,
                                args=(exp_key,)
                            )
                            st.session_state.question_checkboxes[row['id']][str(q_id)] = checkbox_value
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
                                [str(q_id) for q_id in current_question_ids_in_set])
                        ]

                        if not available_questions_df.empty:
                            question_dict_for_multiselect = {
                                q_id: f"{q_text} (Cat: {get_question_category(q_id, questions_df)})" for q_id, q_text in
                                zip(available_questions_df['id'].astype(str), available_questions_df['domanda'])
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
                        on_click=create_save_set_callback(row['id'], exp_key)
                    )

                    # Pulsante Elimina con dialog di conferma
                    if st.button(
                        "Elimina Set",
                        key=f"delete_set_{row['id']}",
                        type="secondary"
                    ):
                        mark_expander_open(exp_key)
                        confirm_delete_set_dialog(row['id'], row['name'])

            # Lo stato dell'expander viene aggiornato tramite i callback

    elif not sets_ready or (st.session_state.question_sets.empty and not selected_categories):
        st.info("Nessun set di domande disponibile. Crea un nuovo set utilizzando la scheda 'Crea Nuovo Set'.")

# Scheda Crea Nuovo Set
with tabs[1]:
    st.header("Crea Nuovo Set di Domande")

    with st.form("create_set_form"):
        set_name = st.text_input("Nome Set", placeholder="Inserisci un nome per il set...")

        selected_qs_for_new_set = []
        questions_ready_for_creation = ('questions' in st.session_state and
                                        not st.session_state.questions.empty and
                                        'domanda' in st.session_state.questions.columns and
                                        'categoria' in st.session_state.questions.columns)

        if questions_ready_for_creation:
            all_questions_df_creation = st.session_state.questions
            question_dict_for_creation = {
                q_id: f"{q_text} (Cat: {get_question_category(q_id, all_questions_df_creation)})" for q_id, q_text in
                zip(all_questions_df_creation['id'].astype(str), all_questions_df_creation['domanda'])
            }

            selected_qs_for_new_set = st.multiselect(
                "Seleziona domande per questo set",
                options=list(question_dict_for_creation.keys()),
                format_func=lambda x: question_dict_for_creation.get(x, x),
                key="create_set_questions",
            )
        else:
            st.info(
                "Nessuna domanda disponibile o dati delle domande non pronti (incl. categorie). Vai a 'Gestione Domande' per aggiungere/caricare domande.")

        submitted = st.form_submit_button("Crea Set")

        if submitted:
            if set_name:
                set_id = create_set(set_name, [str(q_id) for q_id in selected_qs_for_new_set])
                st.session_state.create_set_success_message = f"Set di domande creato con successo con ID: {set_id}"
                st.session_state.create_set_success = True
                st.session_state.trigger_rerun = True
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

    uploaded_file = st.file_uploader("Scegli un file", type=["json", "csv"])

    if uploaded_file is not None:
        st.session_state.uploaded_file_content_set = uploaded_file
        st.button(
            "Importa Set",
            key="import_set_btn",
            on_click=import_set_callback
        )


