import logging
import os

from models.database import DatabaseEngine
from controllers.question_controller import load_questions
from controllers.question_set_controller import load_sets
from controllers.test_controller import load_results
from controllers.openai_client import DEFAULT_MODEL, DEFAULT_ENDPOINT

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """Configura il logger radice con un formato di base."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def get_initial_state() -> dict:
    """Inizializza il database e restituisce lo stato predefinito dell'applicazione."""
    DatabaseEngine.instance().init_db()
    return {
        "questions": load_questions(),
        "question_sets": load_sets(),
        "results": load_results(),
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
        "endpoint": DEFAULT_ENDPOINT,
        "model": DEFAULT_MODEL,
        "temperature": 0.0,
        "max_tokens": 1000,
    }
