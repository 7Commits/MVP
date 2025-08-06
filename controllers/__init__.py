"""Expose controller utilities for external use."""

# API preset management
import logging

from .api_preset_controller import (
    load_presets,
    refresh_api_presets,
    list_presets,
    get_preset_by_id,
    validate_preset,
    save_preset,
    delete_preset,
    test_api_connection,
)

# Question CRUD
from .question_controller import (
    load_questions,
    refresh_questions,
    add_question,
    update_question,
    delete_question,
    filter_questions_by_category,
    import_questions_from_file,
)

# Question set management
from .question_set_controller import (
    load_sets,
    refresh_question_sets,
    create_set,
    update_set,
    delete_set,
    import_sets_from_file,
)

# Results and evaluation utilities
from .test_controller import (
    load_results,
    refresh_results,
    add_result,
    save_results,
    import_results_from_file,
    calculate_statistics,
    evaluate_answer,
    execute_llm_test,
)

# Import helpers
from .startup_controller import get_initial_state
logger = logging.getLogger(__name__)


__all__ = [
    # API preset
    "load_presets",
    "refresh_api_presets",
    "list_presets",
    "get_preset_by_id",
    "validate_preset",
    "save_preset",
    "delete_preset",
    "test_api_connection",
    # Questions
    "load_questions",
    "refresh_questions",
    "add_question",
    "update_question",
    "delete_question",
    "filter_questions_by_category",
    "import_questions_from_file",
    # Question sets
    "load_sets",
    "refresh_question_sets",
    "create_set",
    "update_set",
    "delete_set",
    "import_sets_from_file",
    # Test results
    "load_results",
    "refresh_results",
    "add_result",
    "save_results",
    "import_results_from_file",
    "calculate_statistics",
    "evaluate_answer",
    "execute_llm_test",
    # Startup
    "get_initial_state",
]
