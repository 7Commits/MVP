import logging

import streamlit as st

from controllers import run_test, load_sets, load_presets, get_preset_by_name
from views import register_page
from views.style_utils import add_page_header, add_section_title
logger = logging.getLogger(__name__)


# === FUNZIONI DI CALLBACK ===

def set_llm_mode_callback():
    """Funzione di callback: imposta la modalità LLM"""
    if st.session_state.test_mode != "Valutazione Automatica con LLM":
        st.session_state.test_mode = "Valutazione Automatica con LLM"
        st.session_state.mode_changed = True


def run_llm_test_callback():
    """Funzione di callback: esegue il test LLM"""
    st.session_state.run_llm_test = True


@register_page("Esecuzione Test")
def render():
    # === Inizializzazione delle variabili di stato ===
    if 'test_mode' not in st.session_state:
        st.session_state.test_mode = "Valutazione Automatica con LLM"
    if 'mode_changed' not in st.session_state:
        st.session_state.mode_changed = False
    if 'run_llm_test' not in st.session_state:
        st.session_state.run_llm_test = False

    # Gestisce il cambio di modalità
    if st.session_state.mode_changed:
        st.session_state.mode_changed = False
        st.rerun()

    add_page_header(
        "Esecuzione Test",
        icon="🧪",
        description="Esegui valutazioni automatiche sui tuoi set di domande utilizzando i preset API configurati."
    )

    # Carica i dati necessari, utilizzando cache e session state
    if 'api_presets' not in st.session_state:
        st.session_state.api_presets = load_presets()
    if 'question_sets' not in st.session_state:
        st.session_state.question_sets = load_sets()

    if st.session_state.api_presets.empty:
        st.error(
            "Nessun preset API configurato. Vai alla pagina 'Gestione Preset API' "
            "per crearne almeno uno prima di eseguire i test."
        )
        st.stop()

    # Controlla se ci sono set di domande disponibili
    if st.session_state.question_sets.empty:
        st.warning("Nessun set di domande disponibile. Crea dei set di domande prima di eseguire i test.")
        st.stop()

    # Seleziona set di domande per il test
    add_section_title("Seleziona Set di Domande", icon="📚")
    set_options = {}
    if 'question_sets' in st.session_state and not st.session_state.question_sets.empty:
        for _, row in st.session_state.question_sets.iterrows():
            if 'questions' in row and row['questions']:
                set_options[row['id']] = f"{row['name']} ({len(row['questions'])} domande)"

    if not set_options:
        st.warning("Nessun set di domande con domande associate. Creane uno in 'Gestione Set di Domande'.")
        st.stop()

    selected_set_id = st.selectbox(
        "Seleziona un set di domande",
        options=list(set_options.keys()),
        format_func=lambda x: set_options[x],
        key="select_question_set_for_test"
    )

    selected_set = st.session_state.question_sets[st.session_state.question_sets['id'] == selected_set_id].iloc[0]
    questions_in_set = selected_set['questions']

    # --- Opzioni API basate su Preset ---
    add_section_title("Opzioni API basate su Preset", icon="🛠️")

    preset_display_names = list(st.session_state.api_presets["name"])

    # Seleziona preset per generazione risposta (comune a entrambe le modalità)
    generation_preset_name = st.selectbox(
        "Seleziona Preset per Generazione Risposta LLM",
        options=preset_display_names,
        index=0 if preset_display_names else None,  # Seleziona il primo di default
        key="generation_preset_select",
        help="Il preset API utilizzato per generare la risposta alla domanda."
    )
    st.session_state.selected_generation_preset_name = generation_preset_name

    # Seleziona preset per valutazione (solo per modalità LLM)
    if st.session_state.test_mode == "Valutazione Automatica con LLM":
        evaluation_preset_name = st.selectbox(
            "Seleziona Preset per Valutazione Risposta LLM",
            options=preset_display_names,
            index=0 if preset_display_names else None,  # Seleziona il primo di default
            key="evaluation_preset_select",
            help="Il preset API utilizzato dall'LLM per valutare la similarità e correttezza della risposta generata."
        )
        st.session_state.selected_evaluation_preset_name = evaluation_preset_name

    # --- Logica di Esecuzione Test ---
    test_mode_selected = st.session_state.test_mode

    if test_mode_selected == "Valutazione Automatica con LLM":
        st.header("Esecuzione: Valutazione Automatica con LLM")

        # Pulsante che utilizza la funzione di callback
        st.button(
            "🚀 Esegui Test con LLM",
            key="run_llm_test_btn",
            on_click=run_llm_test_callback
        )

        # Gestisce l'esecuzione del test
        if st.session_state.run_llm_test:
            st.session_state.run_llm_test = False  # Resetta lo stato

            gen_preset_config = get_preset_by_name(
                st.session_state.selected_generation_preset_name,
                st.session_state.api_presets,
            )
            eval_preset_config = get_preset_by_name(
                st.session_state.selected_evaluation_preset_name,
                st.session_state.api_presets,
            )

            if not gen_preset_config or not eval_preset_config:
                st.error("Assicurati di aver selezionato preset validi per generazione e valutazione.")
            else:
                with st.spinner("Generazione risposte e valutazione LLM in corso..."):
                    exec_result = run_test(
                        selected_set_id,
                        selected_set['name'],
                        questions_in_set,
                        gen_preset_config,
                        eval_preset_config,
                    )

                if exec_result:
                    st.session_state.results = exec_result['results_df']
                    st.success(f"Test LLM completato! Punteggio medio: {exec_result['avg_score']:.2f}%")

                    # Visualizzazione risultati dettagliati
                    st.subheader("Risultati Dettagliati")
                    for q_id, result in exec_result['results'].items():
                        with st.expander(
                            f"Domanda: {result['question'][:50]}..."
                        ):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Domanda:**", result['question'])
                                st.write("**Risposta Attesa:**", result['expected_answer'])
                            with col2:
                                st.write("**Risposta Generata:**", result['actual_answer'])
                                st.write("**Punteggio:**", f"{result['evaluation']['score']:.1f}%")
                                st.write("**Valutazione:**", result['evaluation']['explanation'])
