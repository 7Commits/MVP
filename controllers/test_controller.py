"""Funzioni per la gestione dei test e della valutazione tramite LLM."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, IO, List, Tuple, Union

import pandas as pd
from openai import APIConnectionError, APIStatusError, RateLimitError

from models.test_result import TestResult, test_result_importer
from models.question import Question
from utils import openai_client

DEFAULT_MODEL = openai_client.DEFAULT_MODEL

logger = logging.getLogger(__name__)


def load_results() -> pd.DataFrame:
    """Restituisce i risultati dei test utilizzando la cache."""
    return TestResult.load_all_df()


def refresh_results() -> pd.DataFrame:
    """Svuota e ricarica la cache dei risultati dei test."""
    return TestResult.refresh_cache()


def import_results_action(
    uploaded_file: IO[str] | IO[bytes],
) -> Tuple[pd.DataFrame, str]:
    """Importa risultati da ``uploaded_file`` e restituisce il DataFrame aggiornato.

    Parametri
    ---------
    uploaded_file: Oggetto tipo file caricato contenente i risultati.

    Restituisce
    -----------
    Tuple[pd.DataFrame, str]
        Il DataFrame aggiornato dei risultati e un messaggio descrittivo.

    Eccezioni
    ---------
    ValueError
        Se il file non è presente o contiene dati non validi.
    """

    if uploaded_file is None:
        raise ValueError("Nessun file caricato.")

    result = test_result_importer.import_from_file(uploaded_file)
    results = load_results()
    return results, result["message"]


def export_results_action(destination: Union[str, IO[str]]) -> None:
    """Esporta i risultati dei test nella destinazione fornita."""
    test_result_importer.export_to_file(destination)


def generate_answer(question: str, client_config: Dict[str, Any]) -> str:
    """Genera una risposta per ``question`` utilizzando la configurazione LLM fornita.

    Restituisce solo la risposta generata. In caso di errore viene sollevata
    un'eccezione.
    """

    api_key = str(client_config.get("api_key", ""))
    try:
        client = openai_client.get_openai_client(
            api_key=api_key,
            base_url=client_config.get("endpoint"),
        )
    except openai_client.ClientCreationError as exc:
        logger.error(
            "Client API per la generazione risposte non configurato: %s", exc
        )
        raise ValueError("Client API non configurato") from exc

    if question is None or not isinstance(question, str) or question.strip() == "":
        logger.error("La domanda fornita è vuota o non valida.")
        raise ValueError("Domanda vuota o non valida")

    prompt = f"Rispondi alla seguente domanda in modo conciso e accurato: {question}"
    api_request_details = {
        "model": client_config.get("model", DEFAULT_MODEL),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": client_config.get("temperature", 0.7),
        "max_tokens": client_config.get("max_tokens", 500),
    }

    try:
        response = client.chat.completions.create(**api_request_details)
        choices = getattr(response, "choices", None)
        if not choices or not choices[0].message.content:
            raise RuntimeError("Risposta API non valida")
        return choices[0].message.content.strip()
    except (APIConnectionError, RateLimitError, APIStatusError) as e:
        logger.error(
            f"Errore API durante la generazione della risposta di esempio: {type(e).__name__} - {e}"
        )
        raise RuntimeError(str(e)) from e
    except Exception as exc:  # noqa: BLE001
        logger.error(
            f"Errore imprevisto durante la generazione della risposta: {type(exc).__name__} - {exc}"
        )
        raise RuntimeError(str(exc)) from exc


def evaluate_answer(
    question: str,
    expected_answer: str,
    actual_answer: str,
    client_config: Dict[str, Any],
) -> Dict[str, Any]:
    """Valuta ``actual_answer`` rispetto a ``expected_answer`` utilizzando un LLM.

    Restituisce i dati di valutazione come dizionario oppure solleva
    un'eccezione in caso di errore.
    """

    api_key = str(client_config.get("api_key", ""))
    try:
        client = openai_client.get_openai_client(
            api_key=api_key,
            base_url=client_config.get("endpoint"),
        )
    except openai_client.ClientCreationError as exc:
        raise ValueError(
            "Errore: Client API per la valutazione non configurato."
        ) from exc

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
        "model": client_config.get("model", DEFAULT_MODEL),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": client_config.get("temperature", 0.0),
        "max_tokens": client_config.get("max_tokens", 250),
        "response_format": {"type": "json_object"},
    }

    try:
        response = client.chat.completions.create(**api_request_details)
        choices = getattr(response, "choices", None)
        if not choices or not choices[0].message.content:
            logger.error("Risposta API priva di 'choices' validi")
            raise RuntimeError("Risposta API non valida.")
        content = choices[0].message.content
        evaluation = json.loads(content)
        required_keys = [
            "score",
            "explanation",
            "similarity",
            "correctness",
            "completeness",
        ]
        if not all(key in evaluation for key in required_keys):
            raise ValueError(f"Risposta JSON incompleta: {content}")
        return evaluation
    except json.JSONDecodeError as e:
        logger.error(
            f"Errore: Impossibile decodificare la risposta JSON dalla valutazione LLM: {content}"
        )
        raise ValueError(f"Errore di decodifica JSON: {content[:100]}...") from e
    except (APIConnectionError, RateLimitError, APIStatusError) as e:
        logger.error(f"Errore API durante la valutazione: {type(e).__name__} - {e}")
        raise RuntimeError(str(e)) from e
    except Exception as exc:  # noqa: BLE001
        logger.error(
            f"Errore imprevisto durante la valutazione: {type(exc).__name__} - {exc}"
        )
        raise RuntimeError(str(exc)) from exc


def run_test(
    set_id: str,
    set_name: str,
    question_ids: List[str],
    gen_preset_config: dict[str, Any],
    eval_preset_config: dict[str, Any],
) -> dict[str, Any]:
    """Esegue un test generando e valutando risposte con LLM."""

    try:
        questions_map = {str(q.id): q for q in Question.load_all()}
        results: Dict[str, Dict[str, Any]] = {}

        for q_id in question_ids:
            q_obj = questions_map.get(str(q_id))
            if not q_obj:
                continue
            question = q_obj.domanda or ""
            if not question.strip():
                continue
            expected = q_obj.risposta_attesa or "Risposta non disponibile"

            try:
                actual_answer = generate_answer(question, gen_preset_config)
            except Exception as e:  # noqa: BLE001
                error_msg = str(e)
                evaluation = {
                    "score": 0,
                    "explanation": error_msg,
                    "similarity": 0,
                    "correctness": 0,
                    "completeness": 0,
                }
                actual_answer = error_msg
            else:
                try:
                    evaluation = evaluate_answer(
                        question, expected, actual_answer, eval_preset_config
                    )
                except Exception as e:  # noqa: BLE001
                    error_msg = str(e)
                    evaluation = {
                        "score": 0,
                        "explanation": error_msg,
                        "similarity": 0,
                        "correctness": 0,
                        "completeness": 0,
                    }

            results[str(q_id)] = {
                "question": question,
                "expected_answer": expected,
                "actual_answer": actual_answer,
                "evaluation": evaluation,
            }

        stats = TestResult.calculate_statistics(results)
        result_data = {
            "set_name": set_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "avg_score": stats["avg_score"],
            "sample_type": "Generata da LLM",
            "method": "LLM",
            "generation_llm": gen_preset_config.get("model"),
            "evaluation_llm": eval_preset_config.get("model"),
            "questions": results,
            "per_question_scores": stats["per_question_scores"],
            "radar_metrics": stats["radar_metrics"],
        }

        result_id = TestResult.add_and_refresh(set_id, result_data)
        return {
            "result_id": result_id,
            "avg_score": stats["avg_score"],
            "results": results,
            "per_question_scores": stats["per_question_scores"],
            "radar_metrics": stats["radar_metrics"],
            "results_df": TestResult.load_all_df(),
        }
    except Exception as exc:  # noqa: BLE001
        logger.error(
            f"Errore durante l'esecuzione del test LLM: {type(exc).__name__} - {exc}"
        )
        return {}


__all__ = [
    "load_results",
    "refresh_results",
    "import_results_action",
    "generate_answer",
    "evaluate_answer",
    "run_test",
]
