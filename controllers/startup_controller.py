import os

from controllers.db_controller import initialize_database
from services.question_service import load_questions
from controllers.question_set_controller import load_sets
from controllers.test_controller import load_results
from services.openai_service import DEFAULT_MODEL, DEFAULT_ENDPOINT


def get_default_api_settings() -> dict:
    """Restituisce l'endpoint e il modello API predefiniti."""
    return {"model": DEFAULT_MODEL, "endpoint": DEFAULT_ENDPOINT}


def get_initial_state() -> dict:
    """Inizializza il database e restituisce lo stato di default dell'applicazione."""
    initialize_database()
    defaults = get_default_api_settings()
    return {
        "questions": load_questions(),
        "question_sets": load_sets(),
        "results": load_results(),
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
        "endpoint": defaults["endpoint"],
        "model": defaults["model"],
        "temperature": 0.0,
        "max_tokens": 1000,
    }
