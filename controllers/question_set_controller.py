import logging
import os
import json
from typing import List, Optional, Any, Dict, Tuple

import pandas as pd

from .question_controller import add_question_if_not_exists, load_questions
from models.question_set import QuestionSet
from utils.cache import (
    get_question_sets as _get_question_sets,
    refresh_question_sets as _refresh_question_sets,
)

logger = logging.getLogger(__name__)

REQUIRED_CSV_COLUMNS = ["name", "id", "domanda", "risposta_attesa", "categoria"]


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
) -> None:
    """Aggiorna un set di domande esistente e ricarica la cache."""
    QuestionSet.update(set_id, name, question_ids)
    refresh_question_sets()


def delete_set(set_id: str) -> None:
    """Elimina un set di domande e aggiorna la cache."""
    QuestionSet.delete(set_id)
    refresh_question_sets()


def parse_input(uploaded_file) -> List[Dict[str, Any]]:
    """Analizza un file CSV o JSON in una lista di dizionari di set di domande."""
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()

    if file_extension == ".csv":
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:  # pragma: no cover - handled as generic csv error
            raise ValueError("Il formato del file csv non è valido") from e

        missing = [c for c in REQUIRED_CSV_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(
                "Il file CSV deve contenere le colonne " + ", ".join(REQUIRED_CSV_COLUMNS)
            )

        sets_dict: Dict[str, List[Dict[str, str]]] = {}
        for _, row in df.iterrows():
            name = str(row["name"]).strip()
            if not name:
                continue
            question = {
                "id": str(row["id"]).strip() if not pd.isna(row["id"]) else "",
                "domanda": str(row["domanda"]).strip()
                if not pd.isna(row["domanda"])
                else "",
                "risposta_attesa": str(row["risposta_attesa"]).strip()
                if not pd.isna(row["risposta_attesa"])
                else "",
                "categoria": str(row["categoria"]).strip()
                if not pd.isna(row["categoria"])
                else "",
            }
            sets_dict.setdefault(name, []).append(question)
        return [{"name": n, "questions": qs} for n, qs in sets_dict.items()]

    try:
        string_data = uploaded_file.getvalue().decode("utf-8")
        data = json.loads(string_data)
    except Exception as e:  # pragma: no cover - handled as generic json error
        raise ValueError("Il formato del file json non è valido") from e

    if not isinstance(data, list):
        raise ValueError("Il formato del file json non è valido")
    return data


def resolve_question_ids(
    questions_in_set_data: List[Any],
    current_questions: pd.DataFrame,
) -> Tuple[List[str], pd.DataFrame, int, int, List[str]]:
    """Risolve gli identificatori delle domande per un set di domande."""
    warnings: List[str] = []
    question_ids: List[str] = []
    new_added = 0
    existing_found = 0

    for q_idx, q_data in enumerate(questions_in_set_data):
        if isinstance(q_data, dict):
            q_id = str(q_data.get("id", ""))
            q_text = q_data.get("domanda", "")
            q_answer = q_data.get("risposta_attesa", "")
            q_category = q_data.get("categoria", "")
        else:
            q_id = str(q_data)
            q_text = ""
            q_answer = ""
            q_category = ""

        if not q_id:
            warnings.append(f"Domanda #{q_idx + 1} senza ID (saltata).")
            continue

        if q_text and q_answer:
            if q_id in current_questions["id"].astype(str).values:
                existing_found += 1
                question_ids.append(q_id)
            else:
                was_added = add_question_if_not_exists(
                    question_id=q_id,
                    domanda=q_text,
                    risposta_attesa=q_answer,
                    categoria=q_category,
                )
                if was_added:
                    new_added += 1
                    question_ids.append(q_id)
                    new_row = pd.DataFrame(
                        {
                            "id": [q_id],
                            "domanda": [q_text],
                            "risposta_attesa": [q_answer],
                            "categoria": [q_category],
                        }
                    )
                    current_questions = pd.concat(
                        [current_questions, new_row], ignore_index=True
                    )
                else:
                    existing_found += 1
                    question_ids.append(q_id)
            continue

        if q_id in current_questions["id"].astype(str).values:
            existing_found += 1
            question_ids.append(q_id)
        else:
            warnings.append(
                f"Domanda #{q_idx + 1} con ID {q_id} non trovata e senza dettagli; saltata."
            )

    return question_ids, current_questions, new_added, existing_found, warnings


def persist_sets(
    sets_data: List[Dict[str, Any]],
    current_questions: pd.DataFrame,
    current_sets: pd.DataFrame,
) -> Dict[str, Any]:
    """Crea set di domande dai dati analizzati."""
    sets_imported_count = 0
    new_questions_added_count = 0
    existing_questions_found_count = 0
    warnings: List[str] = []

    for set_idx, set_data in enumerate(sets_data):
        if not isinstance(set_data, dict):
            warnings.append(
                f"Elemento #{set_idx + 1} nella lista non è un set valido (saltato)."
            )
            continue

        set_name = set_data.get("name")
        questions_in_set_data = set_data.get("questions", [])

        if not set_name or not isinstance(set_name, str) or not set_name.strip():
            warnings.append(
                f"Set #{set_idx + 1} con nome mancante o non valido (saltato)."
            )
            continue

        if not isinstance(questions_in_set_data, list):
            warnings.append(
                f"Dati delle domande mancanti o non validi per il set '{set_name}' (saltato)."
            )
            continue

        if set_name in current_sets.get("name", pd.Series([])).values:
            warnings.append(
                f"Un set con nome '{set_name}' esiste già. Saltato per evitare duplicati."
            )
            continue

        question_ids, current_questions, added, existing, q_warnings = resolve_question_ids(
            questions_in_set_data, current_questions
        )
        warnings.extend(q_warnings)

        if question_ids or len(questions_in_set_data) == 0:
            try:
                QuestionSet.create(set_name, question_ids)
                sets_imported_count += 1
            except Exception as e:  # pragma: no cover - protective
                warnings.append(
                    f"Errore durante la creazione del set '{set_name}': {e}"
                )
        else:
            warnings.append(
                f"Il set '{set_name}' non è stato creato perché non conteneva domande valide."
            )

        new_questions_added_count += added
        existing_questions_found_count += existing

    sets_df = refresh_question_sets()

    success = sets_imported_count > 0
    success_message = ""
    if success:
        parts = []
        if sets_imported_count > 0:
            parts.append(f"{sets_imported_count} set importati")
        if new_questions_added_count > 0:
            parts.append(f"{new_questions_added_count} nuove domande aggiunte")
        if existing_questions_found_count > 0:
            parts.append(
                f"{existing_questions_found_count} domande esistenti referenziate"
            )
        success_message = ". ".join(parts) + "."

    return {
        "sets_imported_count": sets_imported_count,
        "new_questions_added_count": new_questions_added_count,
        "existing_questions_found_count": existing_questions_found_count,
        "questions_df": current_questions,
        "sets_df": sets_df,
        "warnings": warnings,
        "success": success,
        "success_message": success_message,
    }


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
    except ValueError as e:
        result["error_message"] = str(e)
    except Exception as e:  # pragma: no cover - general protection
        result["error_message"] = f"Errore imprevisto durante l'importazione: {str(e)}"

    return result
