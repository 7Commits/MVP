from typing import List, Optional, Any, Dict
import pandas as pd
import json
import os
from models.question_set import QuestionSet
from controllers.question_controller import (
    add_question_if_not_exists,
    load_questions,
)


def load_sets() -> pd.DataFrame:
    return QuestionSet.load_all()


def create_set(name: str, question_ids: Optional[List[str]] = None) -> str:
    return QuestionSet.create(name, question_ids)


def update_set(set_id: str, name: Optional[str] = None, question_ids: Optional[List[str]] = None) -> None:
    QuestionSet.update(set_id, name, question_ids)


def delete_set(set_id: str) -> None:
    QuestionSet.delete(set_id)


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
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()

        if file_extension == ".csv":
            df = pd.read_csv(uploaded_file)
            required_cols = ["name", "id", "domanda", "risposta_attesa", "categoria"]
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                raise ValueError(
                    "Il file CSV deve contenere le colonne " + ", ".join(required_cols)
                )

            sets_dict: Dict[str, List[Dict[str, str]]] = {}
            for _, row in df.iterrows():
                name = str(row["name"]).strip()
                if not name:
                    continue
                question = {
                    "id": str(row["id"]).strip() if not pd.isna(row["id"]) else "",
                    "domanda": str(row["domanda"]).strip() if not pd.isna(row["domanda"]) else "",
                    "risposta_attesa": str(row["risposta_attesa"]).strip() if not pd.isna(row["risposta_attesa"]) else "",
                    "categoria": str(row["categoria"]).strip() if not pd.isna(row["categoria"]) else "",
                }
                sets_dict.setdefault(name, []).append(question)

            data = [{"name": n, "questions": qs} for n, qs in sets_dict.items()]
        else:
            string_data = uploaded_file.getvalue().decode("utf-8")
            data = json.loads(string_data)

        current_questions = load_questions()
        current_sets = load_sets()

        if not isinstance(data, list):
            result["error_message"] = (
                "Formato JSON non valido. Il file deve contenere una lista (array) di set."
            )
            return result

        sets_imported_count = 0
        new_questions_added_count = 0
        existing_questions_found_count = 0

        for set_idx, set_data in enumerate(data):
            if not isinstance(set_data, dict):
                result["warnings"].append(
                    f"Elemento #{set_idx+1} nella lista non è un set valido (saltato)."
                )
                continue

            set_name = set_data.get("name")
            questions_in_set_data = set_data.get("questions", [])

            if not set_name or not isinstance(set_name, str) or not set_name.strip():
                result["warnings"].append(
                    f"Set #{set_idx+1} con nome mancante o non valido (saltato)."
                )
                continue

            if not isinstance(questions_in_set_data, list):
                result["warnings"].append(
                    f"Dati delle domande mancanti o non validi per il set '{set_name}' (saltato)."
                )
                continue

            if set_name in current_sets["name"].values:
                result["warnings"].append(
                    f"Un set con nome '{set_name}' esiste già. Saltato per evitare duplicati."
                )
                continue

            current_set_question_ids: List[str] = []

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
                    result["warnings"].append(
                        f"Domanda #{q_idx+1} nel set '{set_name}' senza ID (saltata)."
                    )
                    continue

                if q_text and q_answer:
                    if q_id in current_questions["id"].astype(str).values:
                        existing_questions_found_count += 1
                        current_set_question_ids.append(q_id)
                    else:
                        was_added = add_question_if_not_exists(
                            question_id=q_id,
                            domanda=q_text,
                            risposta_attesa=q_answer,
                            categoria=q_category,
                        )
                        if was_added:
                            new_questions_added_count += 1
                            current_set_question_ids.append(q_id)
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
                            existing_questions_found_count += 1
                            current_set_question_ids.append(q_id)
                    continue
                else:
                    if q_id in current_questions["id"].astype(str).values:
                        existing_questions_found_count += 1
                        current_set_question_ids.append(q_id)
                    else:
                        result["warnings"].append(
                            f"Domanda #{q_idx+1} con ID {q_id} nel set '{set_name}' non trovata e senza dettagli; saltata."
                        )

            if current_set_question_ids or len(questions_in_set_data) == 0:
                try:
                    create_set(set_name, current_set_question_ids)
                    sets_imported_count += 1
                except Exception as e:
                    result["warnings"].append(
                        f"Errore durante la creazione del set '{set_name}': {e}"
                    )
            else:
                result["warnings"].append(
                    f"Il set '{set_name}' non è stato creato perché non conteneva domande valide."
                )

        result["questions_df"] = load_questions()
        result["sets_df"] = load_sets()

        if sets_imported_count > 0 or new_questions_added_count > 0:
            success_parts = []
            if sets_imported_count > 0:
                success_parts.append(f"{sets_imported_count} set importati")
            if new_questions_added_count > 0:
                success_parts.append(f"{new_questions_added_count} nuove domande aggiunte")
            if existing_questions_found_count > 0:
                success_parts.append(
                    f"{existing_questions_found_count} domande esistenti referenziate"
                )

            result["success"] = True
            result["success_message"] = ". ".join(success_parts) + "."
        else:
            result["error_message"] = (
                "Nessun set o domanda valida trovata nel file per l'importazione."
            )
    except json.JSONDecodeError:
        result["error_message"] = (
            "Errore di decodifica JSON. Assicurati che il file sia un JSON valido."
        )
    except Exception as e:
        result["error_message"] = f"Errore imprevisto durante l'importazione: {str(e)}"

    return result
