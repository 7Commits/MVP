import logging

from dataclasses import dataclass, field
from typing import Any, Dict, IO, List, Optional, Tuple
import uuid
import pandas as pd
from sqlalchemy import select

from utils.file_reader_utils import read_question_sets
from utils.import_template import ImportTemplate
from utils.export_template import ExportTemplate
from models.database import DatabaseEngine
from models.orm_models import QuestionSetORM, QuestionORM
logger = logging.getLogger(__name__)


@dataclass
class PersistSetsResult:
    """Risultato della funzione ``persist_sets``."""

    sets_df: pd.DataFrame
    questions_df: pd.DataFrame
    sets_imported_count: int
    new_questions_added_count: int
    existing_questions_found_count: int
    warnings: List[str]


@dataclass
class QuestionSet:
    id: str
    name: str
    questions: List[str] = field(default_factory=list)

    @staticmethod
    def load_all() -> List["QuestionSet"]:
        with DatabaseEngine.instance().get_session() as session:
            sets = session.execute(select(QuestionSetORM)).scalars().all()
            return [
                QuestionSet(
                    id=s.id,
                    name=s.name or "",
                    questions=[q.id for q in s.questions],
                )
                for s in sets
            ]

    @staticmethod
    def create(name: str, question_ids: Optional[List[str]] = None) -> str:
        set_id = str(uuid.uuid4())
        q_ids = [str(q) for q in (question_ids or [])]
        with DatabaseEngine.instance().get_session() as session:
            qs = []
            for qid in q_ids:
                q_obj = session.get(QuestionORM, qid)
                if q_obj:
                    qs.append(q_obj)
            qset = QuestionSetORM(id=set_id, name=name, questions=qs)
            session.add(qset)
            session.commit()
        return set_id

    @staticmethod
    def update(set_id: str, name: Optional[str] = None, question_ids: Optional[List[str]] = None) -> None:
        with DatabaseEngine.instance().get_session() as session:
            qset = session.get(QuestionSetORM, set_id)
            if not qset:
                return
            if name is not None:
                qset.name = name
            if question_ids is not None:
                qs = []
                for qid in question_ids:
                    q_obj = session.get(QuestionORM, qid)
                    if q_obj:
                        qs.append(q_obj)
                qset.questions = qs
            session.commit()

    @staticmethod
    def delete(set_id: str) -> None:
        with DatabaseEngine.instance().get_session() as session:
            qset = session.get(QuestionSetORM, set_id)
            if qset:
                session.delete(qset)
            session.commit()

    @staticmethod
    def _resolve_question_ids(
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
                    from controllers.question_controller import (
                        add_question_if_not_exists,
                    )
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

    @staticmethod
    def _persist_entities(
        sets_data: List[Dict[str, Any]],
        current_questions: pd.DataFrame,
        current_sets: pd.DataFrame,
    ) -> "PersistSetsResult":
        """Crea set di domande dai dati analizzati."""
        if not isinstance(sets_data, list):
            raise ValueError("I dati dei set devono essere una lista.")

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

            (
                question_ids,
                current_questions,
                added,
                existing,
                q_warnings,
            ) = QuestionSet._resolve_question_ids(
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

        from utils.cache import refresh_question_sets as _refresh_question_sets
        sets_df = _refresh_question_sets()

        return PersistSetsResult(
            sets_df=sets_df,
            questions_df=current_questions,
            sets_imported_count=sets_imported_count,
            new_questions_added_count=new_questions_added_count,
            existing_questions_found_count=existing_questions_found_count,
            warnings=warnings,
        )

    @staticmethod
    def import_from_file(uploaded_file: IO[str] | IO[bytes]) -> "PersistSetsResult":
        """Deprecated wrapper for compatibility.

        Usa :class:`QuestionSetImporter` per le nuove importazioni.
        """

        if uploaded_file is None:
            raise ValueError("Nessun file fornito per l'importazione.")

        import warnings

        warnings.warn(
            "QuestionSet.import_from_file è deprecato; usa QuestionSetImporter.import_from_file",
            DeprecationWarning,
            stacklevel=2,
        )

        return question_set_importer.import_from_file(uploaded_file)


class QuestionSetImporter(ImportTemplate, ExportTemplate):
    """Importer per i set di domande basato su :class:`ImportTemplate` e :class:`ExportTemplate`."""

    def parse_file(self, file: IO[Any]) -> List[Dict[str, Any]]:  # type: ignore[override]
        """Legge i set di domande dal file usando ``read_question_sets``."""
        return read_question_sets(file)

    def persist_data(self, parsed: List[Dict[str, Any]]) -> PersistSetsResult:  # type: ignore[override]
        """Persiste i dati tramite :meth:`QuestionSet._persist_entities`."""
        from controllers.question_controller import load_questions
        from controllers.question_set_controller import load_sets

        current_questions = load_questions()
        current_sets = load_sets()

        return QuestionSet._persist_entities(parsed, current_questions, current_sets)

    def gather_data(self) -> List[Dict[str, Any]]:  # type: ignore[override]
        """Recupera tutti i set di domande con i dettagli delle domande."""
        from models.question import Question

        sets = QuestionSet.load_all()
        questions = {
            q.id: {"id": q.id, "domanda": q.domanda, "risposta_attesa": q.risposta_attesa, "categoria": q.categoria}
            for q in Question.load_all()
        }
        data: List[Dict[str, Any]] = []
        for s in sets:
            q_list = [questions.get(qid, {"id": qid}) for qid in s.questions]
            data.append({"name": s.name, "questions": q_list})
        return data


question_set_importer = QuestionSetImporter()