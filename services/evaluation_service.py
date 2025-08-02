import json
import logging
from openai import APIConnectionError, RateLimitError, APIStatusError

from services import openai_service

__all__ = ["evaluate_answer"]


def evaluate_answer(
    question: str,
    expected_answer: str,
    actual_answer: str,
    client_config: dict,
    show_api_details: bool = False,
):
    """Valuta una risposta utilizzando un LLM specificato tramite client_config."""
    client = openai_service.get_openai_client(
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
        "model": client_config.get("model", openai_service.DEFAULT_MODEL),
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
                            0 if key != "explanation" else "Valutazione incompleta o formato JSON non corretto."
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
    except Exception as exc:
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
