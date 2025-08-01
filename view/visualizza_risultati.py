import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go

from controllers.test_controller import (
    load_results,
    import_results_from_file,
)
from controllers.question_set_controller import load_sets
from controllers.api_preset_controller import load_presets
from view.style_utils import add_page_header, add_section_title
from view.component_utils import create_card, create_metrics_container

add_page_header(
    "Visualizzazione Risultati Test",
    icon="📊",
    description="Analizza e visualizza i risultati dettagliati delle valutazioni dei test eseguiti."
)

# Carica sempre i risultati direttamente dal database
st.session_state.results = load_results()
if st.session_state.results.empty:
    st.warning("Nessun risultato di test disponibile. Esegui prima alcuni test dalla pagina 'Esecuzione Test'.")
    st.stop()

# Carica sempre i set di domande dal database
st.session_state.question_sets = load_sets()

# Carica sempre i preset API dal database
st.session_state.api_presets = load_presets()

# Stato per messaggi di importazione risultati
if 'import_results_success' not in st.session_state:
    st.session_state.import_results_success = False
if 'import_results_error' not in st.session_state:
    st.session_state.import_results_error = False
if 'import_results_message' not in st.session_state:
    st.session_state.import_results_message = ""

if st.session_state.import_results_success:
    st.success(st.session_state.import_results_message)
    st.session_state.import_results_success = False
if st.session_state.import_results_error:
    st.error(st.session_state.import_results_message)
    st.session_state.import_results_error = False

def get_set_name(set_id):
    if not st.session_state.question_sets.empty:
        set_info = st.session_state.question_sets[st.session_state.question_sets['id'] == str(set_id)]
        if not set_info.empty:
            return set_info.iloc[0]['name']
    return "Set Sconosciuto"

def get_model_from_preset_name(preset_name):
    """Restituisce il modello associato a un preset, se disponibile."""
    if 'api_presets' in st.session_state and not st.session_state.api_presets.empty:
        preset_row = st.session_state.api_presets[st.session_state.api_presets['name'] == str(preset_name)]
        if not preset_row.empty:
            return preset_row.iloc[0]['model']
    return "Sconosciuto"

def import_results_callback():
    """Callback per importare risultati da file JSON."""
    if 'uploaded_results_file' in st.session_state and st.session_state.uploaded_results_file is not None:
        success, message = import_results_from_file(st.session_state.uploaded_results_file)
        st.session_state.import_results_message = message
        st.session_state.import_results_success = success
        st.session_state.import_results_error = not success
        if success:
            st.session_state.results = load_results()
            st.session_state.uploaded_results_file = None

# Filtri per Set e Modello LLM
all_set_names = sorted({get_set_name(r['set_id']) for _, r in st.session_state.results.iterrows()})
all_model_names = sorted({get_model_from_preset_name(r['results'].get('generation_preset')) for _, r in st.session_state.results.iterrows()})

selected_set_filter = st.selectbox(
    "Filtra per Set",
    options=["Tutti"] + all_set_names,
    index=0,
    key="filter_set_name"
)

selected_model_filter = st.selectbox(
    "Filtra per Modello LLM",
    options=["Tutti"] + all_model_names,
    index=0,
    key="filter_model_name"
)

filtered_results_df = st.session_state.results
if selected_set_filter != "Tutti":
    set_ids = st.session_state.question_sets[st.session_state.question_sets['name'] == selected_set_filter]['id'].astype(str)
    filtered_results_df = filtered_results_df[filtered_results_df['set_id'].astype(str).isin(set_ids)]

if selected_model_filter != "Tutti":
    filtered_results_df = filtered_results_df[
        filtered_results_df.apply(
            lambda row: get_model_from_preset_name(row['results'].get('generation_preset')) == selected_model_filter,
            axis=1
        )
    ]

# Elabora i risultati per la visualizzazione nel selectbox
processed_results_for_select = []
for _, row in filtered_results_df.iterrows():
    result_data = row['results'] # Questo è il dizionario che contiene tutti i dettagli
    set_name = get_set_name(row['set_id'])
    avg_score = result_data.get('avg_score', 0)
    method = result_data.get('method', 'N/A')
    method_icon = "🤖" if method == "LLM" else "📊"
    
    processed_results_for_select.append({
        'id': row['id'],
        'display_name': f"{row['timestamp']} - {method_icon} {set_name} (Avg: {avg_score:.2f}%) - {method}"
    })

processed_results_for_select.sort(key=lambda x: x['display_name'].split(' - ')[0], reverse=True) # Ordina per timestamp

result_options = {r['id']: r['display_name'] for r in processed_results_for_select}

# Seleziona il risultato da visualizzare
selected_result_id = st.selectbox(
    "Seleziona un Risultato del Test da Visualizzare",
    options=list(result_options.keys()),
    format_func=lambda x: result_options[x],
    index=0 if result_options else None,
    key="select_test_result_to_view"
)

# Opzionalmente seleziona un secondo risultato per il confronto
# Rimuove l'opzione del risultato attualmente selezionato per evitare di confrontare il test con se stesso
compare_options = [rid for rid in result_options.keys() if rid != selected_result_id]
compare_result_id = st.selectbox(
    "Confronta con un altro risultato (opzionale)",
    options=[None] + compare_options,
    format_func=lambda x: "Nessun confronto" if x is None else result_options[x],
    index=0,
    key="select_test_result_compare"
)
if not selected_result_id:
    st.info("Nessun risultato selezionato o disponibile.")
    st.stop()

# Ottieni i dati del risultato selezionato
selected_result_row = st.session_state.results[st.session_state.results['id'] == selected_result_id].iloc[0]
result_data = selected_result_row['results']
set_name = get_set_name(selected_result_row['set_id'])
questions_results = result_data.get('questions', {})

with st.expander("Esporta/Importa Risultati"):
    col_exp, col_imp = st.columns(2)
    with col_exp:
        selected_json = json.dumps({
            'id': selected_result_row['id'],
            'set_id': selected_result_row['set_id'],
            'timestamp': selected_result_row['timestamp'],
            'results': result_data
        }, indent=2)
        st.download_button(
            "Export Risultato Selezionato",
            selected_json,
            file_name=f"result_{selected_result_row['id']}.json",
            mime="application/json"
        )

        all_json = json.dumps(st.session_state.results.to_dict(orient="records"), indent=2)
        st.download_button(
            "Export Tutti i Risultati",
            all_json,
            file_name="all_results.json",
            mime="application/json"
        )

    with col_imp:
        uploaded_file = st.file_uploader("Seleziona file JSON", type=["json"], key="upload_results")
        if uploaded_file is not None:
            st.session_state.uploaded_results_file = uploaded_file
        st.button(
            "Importa Risultati",
            on_click=import_results_callback,
            key="import_results_btn"
        )

# Carica eventuale risultato di confronto
compare_result_row = None
compare_result_data = None
compare_questions_results = {}
compare_set_name = ""
if compare_result_id:
    compare_result_row = st.session_state.results[st.session_state.results['id'] == compare_result_id].iloc[0]
    compare_result_data = compare_result_row['results']
    compare_questions_results = compare_result_data.get('questions', {})
    compare_set_name = get_set_name(compare_result_row['set_id'])

# Visualizza informazioni generali sul risultato
evaluation_method = result_data.get('method', 'LLM')
method_icon = "🤖" if evaluation_method == "LLM" else "📊"
method_desc = "Valutazione LLM" if evaluation_method == "LLM" else "Metodo sconosciuto"

add_section_title(f"Dettaglio Test: {set_name} [{method_icon} {evaluation_method}]", icon="📄")
st.markdown(f"**ID Risultato:** `{selected_result_id}`")
st.markdown(f"**Eseguito il:** {selected_result_row['timestamp']}")
st.markdown(f"**Metodo di Valutazione:** {method_icon} **{method_desc}**")

if 'generation_preset' in result_data:
    st.markdown(f"**Preset Generazione Risposte:** `{result_data['generation_preset']}`")
if evaluation_method == "LLM" and 'evaluation_preset' in result_data:
    st.markdown(f"**Preset Valutazione Risposte (LLM):** `{result_data['evaluation_preset']}`")


# Metriche Generali del Test
add_section_title("Metriche Generali del Test", icon="📈")

if questions_results:
    avg_score_overall = result_data.get('avg_score', 0)
    num_questions = len(questions_results)
    
    cols_metrics = st.columns(2)
    with cols_metrics[0]:
        st.metric("Punteggio Medio Complessivo", f"{avg_score_overall:.2f}%")
    with cols_metrics[1]:
        st.metric("Numero di Domande Valutate", num_questions)

    if compare_result_row is not None:
        compare_avg = compare_result_data.get('avg_score', 0)
        diff_avg = compare_avg - avg_score_overall
        st.markdown("### Confronto")
        cols_cmp = st.columns(3)
        cols_cmp[0].metric("Punteggio Selezionato", f"{avg_score_overall:.2f}%")
        cols_cmp[1].metric(f"Punteggio Confronto", f"{compare_avg:.2f}%")
        cols_cmp[2].metric("Differenza", f"{diff_avg:+.2f}%")
    
    # Grafico a barre dei punteggi per domanda (mostra anche il risultato di confronto se presente)
    scores_data = []
    all_q_ids = set(questions_results.keys())
    if compare_result_row is not None:
        all_q_ids |= set(compare_questions_results.keys())

    for i, q_id in enumerate(all_q_ids):
        q1 = questions_results.get(q_id)
        q2 = compare_questions_results.get(q_id)
        label = ""
        if q1:
            label = q1.get('question', f'Domanda {i}')
        elif q2:
            label = q2.get('question', f'Domanda {i}')
        label = label[:50] + "..." if len(label) > 50 else label

        if q1:
            scores_data.append({'Domanda': label, 'Punteggio': q1.get('evaluation', {}).get('score', 0), 'Tipo': 'Selezionato'})
        if q2:
            scores_data.append({'Domanda': label, 'Punteggio': q2.get('evaluation', {}).get('score', 0), 'Tipo': 'Confronto'})

    if scores_data:
        df_scores = pd.DataFrame(scores_data)
        fig = px.bar(df_scores, x='Domanda', y='Punteggio', color='Tipo', barmode='group',
                     title="Punteggi per Domanda", height=max(400, len(all_q_ids) * 30))
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

        # Grafico aggiuntivo solo per la modalità LLM
        if evaluation_method == "LLM":
            # Raccogliamo i dati di Somiglianza, Correttezza e Completezza per ogni domanda
            radar_data = []
            metrics_sum = {'similarity': 0, 'correctness': 0, 'completeness': 0}
            count = 0
            
            for q_id, q_data in questions_results.items():
                evaluation = q_data.get('evaluation', {})
                question_text = q_data.get('question', f'Domanda {q_id}')
                # Utilizziamo i primi 20 caratteri della domanda come etichetta
                question_label = question_text[:20] + "..." if len(question_text) > 20 else question_text
                
                # Raccogliamo i dati per il grafico radar individuale
                similarity = evaluation.get('similarity', 0)
                correctness = evaluation.get('correctness', 0)
                completeness = evaluation.get('completeness', 0)
                
                radar_data.append({
                    'Domanda': question_label,
                    'Somiglianza': similarity,
                    'Correttezza': correctness,
                    'Completezza': completeness
                })
                
                # Sommiamo per calcolare le medie
                metrics_sum['similarity'] += similarity
                metrics_sum['correctness'] += correctness
                metrics_sum['completeness'] += completeness
                count += 1
            
            # Calcoliamo le medie per il risultato selezionato
            avg_metrics = {
                'similarity': metrics_sum['similarity'] / count if count > 0 else 0,
                'correctness': metrics_sum['correctness'] / count if count > 0 else 0,
                'completeness': metrics_sum['completeness'] / count if count > 0 else 0
            }

            # Se esiste un risultato di confronto calcoliamo anche le sue medie
            avg_metrics_cmp = None
            if compare_result_row is not None and compare_questions_results:
                cmp_sum = {'similarity': 0, 'correctness': 0, 'completeness': 0}
                cmp_count = 0
                for q_cmp in compare_questions_results.values():
                    eval_cmp = q_cmp.get('evaluation', {})
                    cmp_sum['similarity'] += eval_cmp.get('similarity', 0)
                    cmp_sum['correctness'] += eval_cmp.get('correctness', 0)
                    cmp_sum['completeness'] += eval_cmp.get('completeness', 0)
                    cmp_count += 1
                avg_metrics_cmp = {
                    'similarity': cmp_sum['similarity'] / cmp_count if cmp_count > 0 else 0,
                    'correctness': cmp_sum['correctness'] / cmp_count if cmp_count > 0 else 0,
                    'completeness': cmp_sum['completeness'] / cmp_count if cmp_count > 0 else 0
                }
            
            # Creiamo un DataFrame con i dati
            df_radar = pd.DataFrame(radar_data)
            
            # Prima mostriamo il radar chart per ogni domanda
            categories = ['Somiglianza', 'Correttezza', 'Completezza']
            
            # Creiamo il grafico radar
            fig_radar = go.Figure()

            # Aggiungiamo una traccia per ogni domanda del risultato selezionato
            for i, row in df_radar.iterrows():
                fig_radar.add_trace(go.Scatterpolar(
                    r=[row['Somiglianza'], row['Correttezza'], row['Completezza']],
                    theta=categories,
                    fill='toself',
                    name=row['Domanda']
                ))

            # Traccia media risultato selezionato
            fig_radar.add_trace(go.Scatterpolar(
                r=[avg_metrics['similarity'], avg_metrics['correctness'], avg_metrics['completeness']],
                theta=categories,
                fill='toself',
                name='Media',
                line=dict(color='red', width=3)
            ))

            # Traccia media confronto, se disponibile
            if avg_metrics_cmp is not None:
                fig_radar.add_trace(go.Scatterpolar(
                    r=[avg_metrics_cmp['similarity'], avg_metrics_cmp['correctness'], avg_metrics_cmp['completeness']],
                    theta=categories,
                    fill='toself',
                    name='Media Confronto',
                    line=dict(color='green', width=3, dash='dash')
                ))
            
            # Configuriamo il layout del grafico radar
            fig_radar.update_layout(
                title="Grafico Radar delle Metriche LLM per ogni domanda",
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                ),
                height=600
            )
            
            # Mostriamo il grafico radar
            st.plotly_chart(fig_radar, use_container_width=True)

            # Mostriamo anche i valori medi in un blocco di metriche per maggiore chiarezza
            st.subheader("Valori medi delle metriche")
            cols = st.columns(3)
            cols[0].metric("Somiglianza", f"{avg_metrics['similarity']:.2f}%")
            cols[1].metric("Correttezza", f"{avg_metrics['correctness']:.2f}%")
            cols[2].metric("Completezza", f"{avg_metrics['completeness']:.2f}%")

            if avg_metrics_cmp is not None:
                cols_cmp = st.columns(3)
                cols_cmp[0].metric("Somiglianza (Confronto)", f"{avg_metrics_cmp['similarity']:.2f}%")
                cols_cmp[1].metric("Correttezza (Confronto)", f"{avg_metrics_cmp['correctness']:.2f}%")
                cols_cmp[2].metric("Completezza (Confronto)", f"{avg_metrics_cmp['completeness']:.2f}%")
else:
    st.info("Nessun dettaglio per le domande disponibile in questo risultato.")

if compare_result_row is not None:
    add_section_title("Confronto Dettagliato per Domanda", icon="🔍")
    comparison_rows = []
    all_q_ids = set(questions_results.keys()) | set(compare_questions_results.keys())
    for qid in all_q_ids:
        q1 = questions_results.get(qid, {})
        q2 = compare_questions_results.get(qid, {})
        label = q1.get('question') or q2.get('question') or str(qid)
        score1 = q1.get('evaluation', {}).get('score', None)
        score2 = q2.get('evaluation', {}).get('score', None)
        delta = None
        if score1 is not None and score2 is not None:
            delta = score2 - score1
        comparison_rows.append({
            'Domanda': label[:50] + ('...' if len(label) > 50 else ''),
            'Selezionato': score1,
            'Confronto': score2,
            'Delta': delta
        })
    if comparison_rows:
        df_comp = pd.DataFrame(comparison_rows)
        st.dataframe(df_comp)

# Dettagli per ogni domanda
add_section_title("Risultati Dettagliati per Domanda", icon="📝")
if not questions_results:
    st.info("Nessuna domanda trovata in questo set di risultati.")
else:
    for q_id, q_data in questions_results.items():
        question_text = q_data.get('question', "Testo domanda non disponibile")
        expected_answer = q_data.get('expected_answer', "Risposta attesa non disponibile")
        actual_answer = q_data.get('actual_answer', "Risposta effettiva non disponibile")
        
        with st.expander(
            f"Domanda: {question_text[:100]}..."
        ):
            st.markdown(f"**Domanda:** {question_text}")
            st.markdown(f"**Risposta Attesa:** {expected_answer}")
            st.markdown(f"**Risposta Generata/Effettiva:** {actual_answer}")
            st.divider()
            
            # Mostra Dettagli API di Generazione (se presenti e richiesti)
            generation_api_details = q_data.get('generation_api_details')
            if generation_api_details and isinstance(generation_api_details, dict):
                with st.container():
                    st.markdown("###### Dettagli Chiamata API di Generazione Risposta")
                    if generation_api_details.get('request'):
                        st.caption("Richiesta API Generazione:")
                        st.json(generation_api_details['request'], expanded=False)
                    if generation_api_details.get('response_content'):
                        st.caption("Contenuto Risposta API Generazione:")
                        # Prova a formattare se è una stringa JSON, altrimenti mostra com'è
                        try:
                            response_data_gen = json.loads(generation_api_details['response_content']) if isinstance(generation_api_details['response_content'], str) else generation_api_details['response_content']
                            st.code(json.dumps(response_data_gen, indent=2), language="json")
                        except:
                             st.text(generation_api_details['response_content'])
                    if generation_api_details.get('error'):
                        st.caption("Errore API Generazione:")
                        st.error(generation_api_details['error'])
                st.divider()
            
            if evaluation_method == "LLM":
                evaluation = q_data.get('evaluation', {}) # Assicurati che evaluation sia sempre un dizionario
                st.markdown(f"##### Valutazione LLM")
                score = evaluation.get('score', 0)
                explanation = evaluation.get('explanation', "Nessuna spiegazione.")
                similarity = evaluation.get('similarity', 0)
                correctness = evaluation.get('correctness', 0)
                completeness = evaluation.get('completeness', 0)
                
                st.markdown(f"**Punteggio Complessivo:** {score:.2f}%")
                st.markdown(f"**Spiegazione:** {explanation}")
                
                cols_eval_metrics = st.columns(3)
                cols_eval_metrics[0].metric("Somiglianza", f"{similarity:.2f}%")
                cols_eval_metrics[1].metric("Correttezza", f"{correctness:.2f}%")
                cols_eval_metrics[2].metric("Completezza", f"{completeness:.2f}%")

                api_details = evaluation.get('api_details')
                if api_details and isinstance(api_details, dict):
                    with st.container(): # Sostituisce l'expander interno
                        st.markdown("###### Dettagli Chiamata API di Valutazione")
                        if api_details.get('request'):
                            st.caption("Richiesta API:")
                            st.json(api_details['request'], expanded=False)
                        if api_details.get('response_content'):
                            st.caption("Contenuto Risposta API:")
                            st.code(json.dumps(json.loads(api_details['response_content']), indent=2) if isinstance(api_details['response_content'], str) else json.dumps(api_details['response_content'], indent=2), language="json")
                        if api_details.get('error'):
                            st.caption("Errore API:")
                            st.error(api_details['error'])
            
            st.markdown("--- --- ---")
