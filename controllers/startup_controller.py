import logging

from utils.cache import get_questions, get_question_sets, get_results
from utils.startup_utils import (
    setup_logging,
    initialize_database,
    load_default_config,
)

logger = logging.getLogger(__name__)


def get_initial_state() -> dict:
    """Restituisce lo stato predefinito dell'applicazione."""
    initialize_database()
    defaults = load_default_config()
    cached_data = {
        "questions": get_questions(),
        "question_sets": get_question_sets(),
        "results": get_results(),
    }
    return {**cached_data, **defaults}
