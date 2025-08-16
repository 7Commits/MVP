"""Esporta le utilità dei controller per uso esterno."""

# Gestione dei preset API
import logging

from .api_preset_controller import (
    load_presets,
    refresh_api_presets,
    list_presets,
    get_preset_by_id,
    get_preset_by_name,
    validate_preset,
    save_preset,
    delete_preset,
    test_api_connection,
)

# Operazioni CRUD sulle domande
from .question_controller import (
    load_questions,
    refresh_questions,
    add_question,
    update_question,
    delete_question,
    get_filtered_questions,
    save_question_action,
    delete_question_action,
    import_questions_action,
    get_question_text,
    get_question_category,
    export_questions_action,
)

# Gestione dei set di domande
from .question_set_controller import (
    load_sets,
    refresh_question_sets,
    create_set,
    update_set,
    delete_set,
    prepare_sets_for_view,
    export_sets_action,
)

# Risultati e utilità di valutazione
from .test_controller import (
    load_results,
    refresh_results,
    import_results_action,
    export_results_action,
    generate_answer,
    evaluate_answer,
    run_test,
)

from .result_controller import (
    get_results,
    list_set_names,
    list_model_names,
    prepare_select_options,
)

from models.test_result import TestResult

calculate_statistics = TestResult.calculate_statistics

# Funzioni di avvio
from .startup_controller import get_initial_state
logger = logging.getLogger(__name__)


__all__ = [
    # Preset API
    "load_presets",
    "refresh_api_presets",
    "list_presets",
    "get_preset_by_id",
    "get_preset_by_name",
    "validate_preset",
    "save_preset",
    "delete_preset",
    "test_api_connection",
    # Domande
    "load_questions",
    "refresh_questions",
    "add_question",
    "update_question",
    "delete_question",
    "get_filtered_questions",
    "save_question_action",
    "delete_question_action",
    "import_questions_action",
    "get_question_text",
    "get_question_category",
    "export_questions_action",
    # Set di domande
    "load_sets",
    "refresh_question_sets",
    "create_set",
    "update_set",
    "delete_set",
    "prepare_sets_for_view",
    "export_sets_action",
    # Risultati dei test
    "load_results",
    "refresh_results",
    "import_results_action",
    "export_results_action",
    "generate_answer",
    "evaluate_answer",
    "calculate_statistics",
    "run_test",
    "get_results",
    "list_set_names",
    "list_model_names",
    "prepare_select_options",
    # Avvio
    "get_initial_state",
]
