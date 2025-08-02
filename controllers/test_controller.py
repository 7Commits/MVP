import pandas as pd
from typing import Dict, Tuple, List
import json
import uuid
from datetime import datetime
from models.test_result import TestResult
from services.cache import (
    get_results as _get_results,
    refresh_results as _refresh_results,
)
from controllers.openai_controller import (
    evaluate_answer,
    generate_example_answer_with_llm,
)
from services.question_service import load_questions


def load_results() -> pd.DataFrame:
    """Restituisce i risultati dei test utilizzando la cache."""
    return _get_results()


def refresh_results() -> pd.DataFrame:
    """Svuota e ricarica la cache dei risultati dei test."""
    return _refresh_results()


def add_result(set_id: str, results_data: Dict) -> str:
    rid = TestResult.add(set_id, results_data)
    _refresh_results()
    return rid


def save_results(df: pd.DataFrame) -> None:
    TestResult.save_df(df)
    _refresh_results()


def import_results_from_file(file) -> Tuple[bool, str]:
    """Importa risultati di test da un file JSON."""
    try:
        data = json.load(file)
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            return False, "Il file JSON deve contenere un oggetto o una lista di risultati."

        results_df = load_results()
        added_count = 0

        for item in data:
            if not isinstance(item, dict):
                continue

            result_id = str(item.get('id', uuid.uuid4()))
            if result_id in results_df['id'].astype(str).values:
                continue

            set_id = str(item.get('set_id', ''))
            timestamp = str(item.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            results_content = item.get('results', {})

            new_row = {
                'id': result_id,
                'set_id': set_id,
                'timestamp': timestamp,
                'results': results_content if isinstance(results_content, dict) else {}
            }

            results_df = pd.concat([results_df, pd.DataFrame([new_row])], ignore_index=True)
            added_count += 1

        if added_count > 0:
            save_results(results_df)
            message = f"Importati {added_count} risultati."
        else:
            message = "Nessun nuovo risultato importato."

        return True, message
    except Exception as e:
        return False, f"Errore durante l'importazione dei risultati: {str(e)}"


def calculate_statistics(questions_results: Dict[str, Dict]) -> Dict:
    """Calcola statistiche dai risultati grezzi delle domande."""
    if not questions_results:
        return {
            "avg_score": 0,
            "per_question_scores": [],
            "radar_metrics": {
                "similarity": 0,
                "correctness": 0,
                "completeness": 0,
            },
        }

    per_question_scores: List[Dict] = []
    radar_sums = {"similarity": 0, "correctness": 0, "completeness": 0}

    for qid, qdata in questions_results.items():
        evaluation = qdata.get("evaluation", {})
        score = evaluation.get("score", 0)
        per_question_scores.append({
            "question": qdata.get("question", f"Domanda {qid}"),
            "score": score,
        })
        for metric in radar_sums.keys():
            radar_sums[metric] += evaluation.get(metric, 0)

    count = len(per_question_scores)
    avg_score = (
        sum(item["score"] for item in per_question_scores) / count if count > 0 else 0
    )
    radar_metrics = {
        metric: radar_sums[metric] / count if count > 0 else 0 for metric in radar_sums
    }

    return {
        "avg_score": avg_score,
        "per_question_scores": per_question_scores,
        "radar_metrics": radar_metrics,
    }


def execute_llm_test(
    set_id: str,
    set_name: str,
    question_ids: List[str],
    gen_preset_config: Dict,
    eval_preset_config: Dict,
    show_api_details: bool = False,
) -> Dict:
    """
    Esegue la generazione delle risposte e la valutazione tramite LLM per
    un elenco di domande. Restituisce i dettagli dei risultati e aggiorna
    la cache dei risultati salvati.
    """
    questions_df = load_questions()

    def get_question_data(qid: str):
        row = questions_df[questions_df['id'] == str(qid)]
        if row.empty:
            return None
        question = row.iloc[0].get('domanda', row.iloc[0].get('question', ''))
        expected = row.iloc[0].get('risposta_attesa', row.iloc[0].get('expected_answer', ''))
        if not question or not isinstance(question, str) or question.strip() == "":
            return None
        if not expected or not isinstance(expected, str) or expected.strip() == "":
            expected = "Risposta non disponibile"
        return {'question': question, 'expected_answer': expected}

    results: Dict = {}
    for q_id in question_ids:
        q_data = get_question_data(q_id)
        if not q_data:
            continue
        generation_output = generate_example_answer_with_llm(
            q_data['question'],
            client_config=gen_preset_config,
            show_api_details=show_api_details,
        )
        actual_answer = generation_output.get('answer')
        generation_api_details = generation_output.get('api_details')

        if actual_answer is None:
            results[q_id] = {
                'question': q_data['question'],
                'expected_answer': q_data['expected_answer'],
                'actual_answer': 'Errore Generazione',
                'evaluation': {'score': 0, 'explanation': 'Generazione fallita'},
                'generation_api_details': generation_api_details,
            }
            continue

        evaluation = evaluate_answer(
            q_data['question'],
            q_data['expected_answer'],
            actual_answer,
            client_config=eval_preset_config,
            show_api_details=show_api_details,
        )
        results[q_id] = {
            'question': q_data['question'],
            'expected_answer': q_data['expected_answer'],
            'actual_answer': actual_answer,
            'evaluation': evaluation,
            'generation_api_details': generation_api_details,
        }

    if not results:
        return {}

    avg_score = sum(r['evaluation']['score'] for r in results.values()) / len(results)
    result_data = {
        'set_name': set_name,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'avg_score': avg_score,
        'sample_type': 'Generata da LLM',
        'method': 'LLM',
        'generation_llm': gen_preset_config.get('model'),
        'evaluation_llm': eval_preset_config.get('model'),
        'questions': results,
    }

    result_id = add_result(set_id, result_data)
    results_df = load_results()

    return {
        'result_id': result_id,
        'avg_score': avg_score,
        'results': results,
        'results_df': results_df,
    }
