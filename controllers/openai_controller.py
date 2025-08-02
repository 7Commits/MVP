import logging
from openai import APIConnectionError, RateLimitError, APIStatusError

from services import evaluation_service, openai_service

__all__ = [
    "evaluate_answer",
    "generate_example_answer_with_llm",
    "test_api_connection",
]


def evaluate_answer(
    question: str,
    expected_answer: str,
    actual_answer: str,
    client_config: dict,
    show_api_details: bool = False,
):
    """Delega la valutazione della risposta a services.evaluation_service."""
    return evaluation_service.evaluate_answer(
        question, expected_answer, actual_answer, client_config, show_api_details
    )


def generate_example_answer_with_llm(
    question: str, client_config: dict, show_api_details: bool = False
):
    """Genera una risposta di esempio per una domanda utilizzando un LLM."""
    client = openai_service.get_openai_client(
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
        logging.error("La domanda fornita \u00e8 vuota o non valida.")
        return {
            "answer": None,
            "api_details": {"error": "Domanda vuota o non valida"}
            if show_api_details
            else None,
        }

    prompt = f"Rispondi alla seguente domanda in modo conciso e accurato: {question}"

    api_request_details = {
        "model": client_config.get("model", openai_service.DEFAULT_MODEL),
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
    except Exception as exc:
        logging.error(
            f"Errore imprevisto durante la generazione della risposta: {type(exc).__name__} - {exc}"
        )
        if show_api_details:
            api_details_for_log["error"] = str(exc)
        return {
            "answer": None,
            "api_details": api_details_for_log if show_api_details else None,
        }


def test_api_connection(
    api_key: str, endpoint: str, model: str, temperature: float, max_tokens: int
):
    """Testa la connessione all'API LLM con i parametri forniti."""
    client = openai_service.get_openai_client(api_key=api_key, base_url=endpoint)
    if not client:
        return False, "Client API non inizializzato. Controlla chiave API e endpoint."

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "Test connessione. Rispondi solo con: 'Connessione riuscita.'",
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content or ""
        if "Connessione riuscita." in content:
            return True, "Connessione API riuscita!"
        else:
            return (
                False,
                "Risposta inattesa dall'API (potrebbe indicare un problema con il modello o l'endpoint): "
                f"{content[:200]}...",
            )
    except APIConnectionError as e:
        return False, f"Errore di connessione API: {e}"
    except RateLimitError as e:
        return False, f"Errore di Rate Limit API: {e}"
    except APIStatusError as e:
        return (
            False,
            "Errore di stato API (es. modello '{model}' non valido per l'endpoint '{endpoint}', "
            f"autenticazione fallita, quota superata): {e.status_code} - {e.message}",
        )
    except Exception as exc:
        return False, (
            f"Errore imprevisto durante il test della connessione: {type(exc).__name__} - {exc}"
        )
