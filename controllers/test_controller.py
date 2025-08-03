"""Funzioni per la gestione dei test e della valutazione tramite LLM."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd
from openai import APIConnectionError, APIStatusError, RateLimitError

from models.question import Question
from models.test_result import TestResult
from . import openai_client
from utils.cache import (
    get_results as _get_results,
    refresh_results as _refresh_results,
)


def load_results() -> pd.DataFrame:
    """Restituisce i risultati dei test utilizzando la cache."""

    return _get_results()


def refresh_results() -> pd.DataFrame:
    """Svuota e ricarica la cache dei risultati dei test."""

    return _refresh_results()


def add_result(set_id: str, results_data: Dict) -> str:
    """Aggiunge un nuovo risultato di test e aggiorna la cache."""

    rid = TestResult.add(set_id, results_data)
    refresh_results()
    return rid


def save_results(df: pd.DataFrame) -> None:
    """Salva il DataFrame dei risultati e aggiorna la cache."""

    TestResult.save_df(df)
    refresh_results()


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

            result_id = str(item.get("id", uuid.uuid4()))
            if result_id in results_df["id"].astype(str).values:
                continue

            set_id = str(item.get("set_id", ""))
            timestamp = str(
                item.get(
                    "timestamp",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
            )
            results_content = item.get("results", {})

            new_row = {
                "id": result_id,
                "set_id": set_id,
                "timestamp": timestamp,
                "results": results_content if isinstance(results_content, dict) else {},
            }

            results_df = pd.concat(
                [results_df, pd.DataFrame([new_row])], ignore_index=True
            )
            added_count += 1

        if added_count > 0:
            save_results(results_df)
            message = f"Importati {added_count} risultati."
        else:
            message = "Nessun nuovo risultato importato."

        return True, message
    except Exception as e:  # noqa: BLE001
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
        per_question_scores.append(
            {"question": qdata.get("question", f"Domanda {qid}"), "score": score}
        )
        for metric in radar_sums.keys():
            radar_sums[metric] += evaluation.get(metric, 0)

    count = len(per_question_scores)
    avg_score = (
        sum(item["score"] for item in per_question_scores) / count if count > 0 else 0
    )
    radar_metrics = {
        metric: radar_sums[metric] / count if count > 0 else 0
        for metric in radar_sums
    }

    return {
        "avg_score": avg_score,
        "per_question_scores": per_question_scores,
        "radar_metrics": radar_metrics,
    }


def evaluate_answer(
    question: str,
    expected_answer: str,
    actual_answer: str,
    client_config: dict,
    show_api_details: bool = False,
):
    """Valuta una risposta utilizzando un LLM specificato tramite client_config."""

    client = openai_client.get_openai_client(
        api_key=client_config.get("api_key"),
        base_url=client_config.get("endpoint"),
    )
    if not client:
        return {
            "score": 0,
            "explanation": "Errore: Client API per la valutazione non configurato.",
            "similarity": 0,
            "correctness": 0,
            "completeness": 0,
        }

    prompt = f"""
        Sei un valutatore esperto che valuta la qualità delle risposte alle domande.
        Domanda: {question}
        Risposta Attesa: {expected_answer}
        Risposta Effettiva: {actual_answer}

        Valuta la risposta effettiva rispetto alla risposta attesa in base a:
        1. Somiglianza (0-100): Quanto è semanticamente simile la risposta effettiva a quella attesa?
        2. Correttezza (0-100): Le informazioni nella risposta effettiva sono fattualmente corrette?
        3. Completezza (0-100): La risposta effettiva contiene tutti i punti chiave della risposta attesa?
        Calcola un punteggio complessivo (0-100) basato su queste metriche.
        Fornisci una breve spiegazione della tua valutazione (max 100 parole).
        Formatta la tua risposta come un oggetto JSON con questi campi:
        - score: il punteggio complessivo (numero)
        - explanation: la tua spiegazione (stringa)
        - similarity: punteggio di somiglianza (numero)
        - correctness: punteggio di correttezza (numero)
        - completeness: punteggio di completezza (numero)
        Esempio di risposta JSON:
        {{
            "score": 95,
            "explanation": "La risposta è corretta e completa",
            "similarity": 90,
            "correctness": 100,
            "completeness": 95
        }}
    """

    api_request_details = {
        "model": client_config.get("model", openai_client.DEFAULT_MODEL),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": client_config.get("temperature", 0.0),
        "max_tokens": client_config.get("max_tokens", 250),
        "response_format": {"type": "json_object"},
    }

    api_details_for_log = {}
    if show_api_details:
        api_details_for_log["request"] = api_request_details.copy()

    try:
        response = client.chat.completions.create(**api_request_details)
        choices = getattr(response, "choices", None)
        if not choices:
            logging.error("Risposta API priva di 'choices' validi")
            if show_api_details:
                api_details_for_log["response_content"] = ""
            return {
                "score": 0,
                "explanation": "Errore: risposta API non valida.",
                "similarity": 0,
                "correctness": 0,
                "completeness": 0,
                "api_details": api_details_for_log,
            }
        content = choices[0].message.content or "{}"
        if show_api_details:
            api_details_for_log["response_content"] = content

        try:
            evaluation = json.loads(content)
            required_keys = [
                "score",
                "explanation",
                "similarity",
                "correctness",
                "completeness",
            ]
            if not all(key in evaluation for key in required_keys):
                logging.warning(
                    f"Risposta JSON dalla valutazione LLM incompleta: {content}. Verranno usati valori di default."
                )
                for key in required_keys:
                    if key not in evaluation:
                        evaluation[key] = (
                            0
                            if key != "explanation"
                            else "Valutazione incompleta o formato JSON non corretto."
                        )

            evaluation["api_details"] = api_details_for_log
            return evaluation
        except json.JSONDecodeError:
            logging.error(
                f"Errore: Impossibile decodificare la risposta JSON dalla valutazione LLM: {content}"
            )
            return {
                "score": 0,
                "explanation": f"Errore di decodifica JSON: {content[:100]}...",
                "similarity": 0,
                "correctness": 0,
                "completeness": 0,
                "api_details": api_details_for_log,
            }

    except (APIConnectionError, RateLimitError, APIStatusError) as e:
        logging.error(f"Errore API durante la valutazione: {type(e).__name__} - {e}")
        api_details_for_log["error"] = str(e)
        return {
            "score": 0,
            "explanation": f"Errore API: {type(e).__name__}",
            "similarity": 0,
            "correctness": 0,
            "completeness": 0,
            "api_details": api_details_for_log,
        }
    except Exception as exc:  # noqa: BLE001
        logging.error(
            f"Errore imprevisto durante la valutazione: {type(exc).__name__} - {exc}"
        )
        api_details_for_log["error"] = str(exc)
        return {
            "score": 0,
            "explanation": f"Errore imprevisto: {type(exc).__name__}",
            "similarity": 0,
            "correctness": 0,
            "completeness": 0,
            "api_details": api_details_for_log,
        }


def generate_example_answer_with_llm(
    question: str, client_config: dict, show_api_details: bool = False
):
    """Genera una risposta di esempio per una domanda utilizzando un LLM."""

    client = openai_client.get_openai_client(
        api_key=client_config.get("api_key"),
        base_url=client_config.get("endpoint"),
    )
    if not client:
        logging.error("Client API per la generazione risposte non configurato.")
        return {
            "answer": None,
            "api_details": {"error": "Client API non configurato"}
            if show_api_details
            else None,
        }

    if question is None or not isinstance(question, str) or question.strip() == "":
        logging.error("La domanda fornita è vuota o non valida.")
        return {
            "answer": None,
            "api_details": {"error": "Domanda vuota o non valida"}
            if show_api_details
            else None,
        }

    prompt = f"Rispondi alla seguente domanda in modo conciso e accurato: {question}"

    api_request_details = {
        "model": client_config.get("model", openai_client.DEFAULT_MODEL),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": client_config.get("temperature", 0.7),
        "max_tokens": client_config.get("max_tokens", 500),
    }

    api_details_for_log = {}
    if show_api_details:
        api_details_for_log["request"] = api_request_details.copy()

    try:
        response = client.chat.completions.create(**api_request_details)
        answer = (
            response.choices[0].message.content.strip()
            if response.choices and response.choices[0].message.content
            else None
        )
        if show_api_details:
            api_details_for_log["response_content"] = (
                response.choices[0].message.content
                if response.choices
                else "Nessun contenuto"
            )
        return {
            "answer": answer,
            "api_details": api_details_for_log if show_api_details else None,
        }

    except (APIConnectionError, RateLimitError, APIStatusError) as e:
        logging.error(
            f"Errore API durante la generazione della risposta di esempio: {type(e).__name__} - {e}"
        )
        if show_api_details:
            api_details_for_log["error"] = str(e)
        return {
            "answer": None,
            "api_details": api_details_for_log if show_api_details else None,
        }
    except Exception as exc:  # noqa: BLE001
        logging.error(
            f"Errore imprevisto durante la generazione della risposta: {type(exc).__name__} - {exc}"
        )
        if show_api_details:
            api_details_for_log["error"] = str(exc)
        return {
            "answer": None,
            "api_details": api_details_for_log if show_api_details else None,
        }


def execute_llm_test(
    set_id: str,
    set_name: str,
    question_ids: List[str],
    gen_preset_config: Dict,
    eval_preset_config: Dict,
    show_api_details: bool = False,
) -> Dict:
    """Esegue la generazione e valutazione delle risposte tramite LLM."""

    questions = [
        {"id": q.id, "question": q.domanda, "expected_answer": q.risposta_attesa}
        for q in Question.load_all()
    ]
    questions_df = pd.DataFrame(questions)

    def get_question_data(qid: str):
        row = questions_df[questions_df["id"] == str(qid)]
        if row.empty:
            return None
        question = row.iloc[0].get("question", "")
        expected = row.iloc[0].get("expected_answer", "")
        if not question or not isinstance(question, str) or question.strip() == "":
            return None
        if not expected or not isinstance(expected, str) or expected.strip() == "":
            expected = "Risposta non disponibile"
        return {"question": question, "expected_answer": expected}

    results: Dict = {}
    for q_id in question_ids:
        q_data = get_question_data(q_id)
        if not q_data:
            continue
        generation_output = generate_example_answer_with_llm(
            q_data["question"],
            client_config=gen_preset_config,
            show_api_details=show_api_details,
        )
        actual_answer = generation_output.get("answer")
        generation_api_details = generation_output.get("api_details")

        if actual_answer is None:
            results[q_id] = {
                "question": q_data["question"],
                "expected_answer": q_data["expected_answer"],
                "actual_answer": "Errore Generazione",
                "evaluation": {"score": 0, "explanation": "Generazione fallita"},
                "generation_api_details": generation_api_details,
            }
            continue

        evaluation = evaluate_answer(
            q_data["question"],
            q_data["expected_answer"],
            actual_answer,
            client_config=eval_preset_config,
            show_api_details=show_api_details,
        )
        results[q_id] = {
            "question": q_data["question"],
            "expected_answer": q_data["expected_answer"],
            "actual_answer": actual_answer,
            "evaluation": evaluation,
            "generation_api_details": generation_api_details,
        }

    if not results:
        return {}

    avg_score = sum(r["evaluation"]["score"] for r in results.values()) / len(results)
    result_data = {
        "set_name": set_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "avg_score": avg_score,
        "sample_type": "Generata da LLM",
        "method": "LLM",
        "generation_llm": gen_preset_config.get("model"),
        "evaluation_llm": eval_preset_config.get("model"),
        "questions": results,
    }

    result_id = add_result(set_id, result_data)
    results_df = load_results()

    return {
        "result_id": result_id,
        "avg_score": avg_score,
        "results": results,
        "results_df": results_df,
    }


__all__ = [
    "load_results",
    "refresh_results",
    "add_result",
    "save_results",
    "import_results_from_file",
    "calculate_statistics",
    "evaluate_answer",
    "generate_example_answer_with_llm",
    "execute_llm_test",
]
