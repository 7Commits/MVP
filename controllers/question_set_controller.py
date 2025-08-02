from typing import List, Optional, Any, Dict
import pandas as pd
import json
import os
from models.question_set import QuestionSet
from services.question_service import load_questions
from services.cache import (
    get_question_sets as _get_question_sets,
    refresh_question_sets as _refresh_question_sets,
)
from services.question_set_importer import parse_input, persist_sets


def load_sets() -> pd.DataFrame:
    """Restituisce tutti i set di domande utilizzando la cache."""
    return _get_question_sets()


def refresh_question_sets() -> pd.DataFrame:
    """Svuota e ricarica la cache dei set di domande."""
    return _refresh_question_sets()


def create_set(name: str, question_ids: Optional[List[str]] = None) -> str:
    set_id = QuestionSet.create(name, question_ids)
    _refresh_question_sets()
    return set_id


def update_set(set_id: str, name: Optional[str] = None, question_ids: Optional[List[str]] = None) -> None:
    QuestionSet.update(set_id, name, question_ids)
    _refresh_question_sets()


def delete_set(set_id: str) -> None:
    QuestionSet.delete(set_id)
    _refresh_question_sets()


def import_sets_from_file(uploaded_file) -> Dict[str, Any]:
    """Importa uno o più set di domande da un file JSON o CSV."""
    result: Dict[str, Any] = {
        "success": False,
        "success_message": "",
        "error_message": "",
        "questions_df": None,
        "sets_df": None,
        "warnings": [],
    }

    if uploaded_file is None:
        result["error_message"] = "Nessun file fornito per l'importazione."
        return result

    try:
        data = parse_input(uploaded_file)
        current_questions = load_questions()
        current_sets = load_sets()
        persist_result = persist_sets(data, current_questions, current_sets)

        result.update(
            {
                "success": persist_result["success"],
                "success_message": persist_result["success_message"],
                "questions_df": persist_result["questions_df"],
                "sets_df": persist_result["sets_df"],
                "warnings": persist_result["warnings"],
            }
        )
        if not persist_result["success"]:
            result["error_message"] = (
                "Nessun set o domanda valida trovata nel file per l'importazione."
            )
    except json.JSONDecodeError:
        result["error_message"] = (
            "Errore di decodifica JSON. Assicurati che il file sia un JSON valido."
        )
    except ValueError as e:
        result["error_message"] = str(e)
    except Exception as e:
        result["error_message"] = f"Errore imprevisto durante l'importazione: {str(e)}"

    return result
