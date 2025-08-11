import logging

from utils.cache import get_questions, get_question_sets, get_results
from utils.startup_utils import (
    DefaultConfig,
    initialize_database,
    load_default_config,
    setup_logging,
)

logger = logging.getLogger(__name__)


def get_initial_state() -> dict[str, object]:
    """Restituisce lo stato predefinito dell'applicazione."""
    initialize_database()
    defaults: DefaultConfig = load_default_config()
    cached_data: dict[str, object] = {
        "questions": get_questions(),
        "question_sets": get_question_sets(),
        "results": get_results(),
    }
    return {**cached_data, **defaults}
