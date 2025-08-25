import logging
from typing import List, Optional, Any, Dict, IO, Union

import pandas as pd

from models.question_set import QuestionSet, question_set_importer # PersistSetsResult not used
from utils.cache import (
    get_questions as _get_questions,
    get_question_sets as _get_question_sets,
    refresh_question_sets as _refresh_question_sets,
)
from utils.data_format_utils import (
    build_questions_detail,
    format_questions_for_view,
)
logger = logging.getLogger(__name__)


def load_sets() -> pd.DataFrame:
    """Restituisce tutti i set di domande utilizzando la cache."""
    return _get_question_sets()


def refresh_question_sets() -> pd.DataFrame:
    """Svuota e ricarica la cache dei set di domande."""
    return _refresh_question_sets()


def create_set(name: str, question_ids: Optional[List[str]] = None) -> str:
    """Crea un nuovo set di domande e aggiorna la cache."""
    set_id = QuestionSet.create(name, question_ids)
    refresh_question_sets()
    return set_id


def update_set(
    set_id: str,
    name: Optional[str] = None,
    question_ids: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Aggiorna un set di domande esistente e ricarica la cache.

    Restituisce il DataFrame aggiornato dei set di domande."""
    QuestionSet.update(set_id, name, question_ids)
    return refresh_question_sets()


def delete_set(set_id: str) -> pd.DataFrame:
    """Elimina un set di domande e aggiorna la cache.

    Restituisce il DataFrame aggiornato dei set di domande."""
    QuestionSet.delete(set_id)
    return refresh_question_sets()


def export_sets_action(destination: Union[str, IO[str]]) -> None:
    """Esporta tutti i set di domande nella destinazione indicata."""
    question_set_importer.export_to_file(destination)


def prepare_sets_for_view(
    selected_categories: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Prepara le informazioni dei set e delle domande per la vista."""
    try:
        questions_df_raw = _get_questions()
        sets_df = _get_question_sets()

        questions_df, question_map, categories = format_questions_for_view(
            questions_df_raw
        )

        if sets_df.empty:
            sets_df = pd.DataFrame(
                columns=["id", "name", "questions", "questions_detail"]
            )
        else:
            sets_df = sets_df.copy()
            sets_df["questions_detail"] = sets_df["questions"].apply(
                lambda q_ids: build_questions_detail(question_map, q_ids)
            )

        filtered_sets_df = sets_df
        if selected_categories:
            def has_categories(details: List[Dict[str, Any]]) -> bool:
                categories_in_set = {d.get("categoria") for d in details}
                return all(cat in categories_in_set for cat in selected_categories)

            filtered_sets_df = sets_df[
                sets_df["questions_detail"].apply(has_categories)
            ]

        return {
            "questions_df": questions_df,
            "sets_df": filtered_sets_df,
            "raw_sets_df": sets_df,
            "categories": categories,
        }
    except Exception as exc:  # pragma: no cover - error path
        logger.error("Errore nella preparazione dei set: %s", exc)
        return {
            "questions_df": pd.DataFrame(
                columns=["id", "domanda", "risposta_attesa", "categoria"]
            ),
            "sets_df": pd.DataFrame(
                columns=["id", "name", "questions", "questions_detail"]
            ),
            "raw_sets_df": pd.DataFrame(
                columns=["id", "name", "questions", "questions_detail"]
            ),
            "categories": [],
        }
