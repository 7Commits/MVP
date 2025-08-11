import logging

from dataclasses import dataclass
from typing import IO, List, Optional, Tuple, Dict, Any, cast
import uuid
import pandas as pd
from sqlalchemy import select, delete
from sqlalchemy.orm import Mapper

from models.database import DatabaseEngine
from models.orm_models import QuestionORM, question_set_questions
from utils.data_format_utils import format_questions_for_view
from utils.file_reader_utils import read_questions, filter_new_rows
logger = logging.getLogger(__name__)


@dataclass
class Question:
    id: str
    domanda: str
    risposta_attesa: str
    categoria: str = ""

    @staticmethod
    def load_all() -> List["Question"]:
        with DatabaseEngine.instance().get_session() as session:
            results = session.execute(select(QuestionORM)).scalars().all()
            return [
                Question(
                    id=q.id,
                    domanda=q.domanda or "",
                    risposta_attesa=q.risposta_attesa or "",
                    categoria=q.categoria or "",
                )
                for q in results
            ]

    @staticmethod
    def add(domanda: str, risposta_attesa: str, categoria: str = "", question_id: Optional[str] = None) -> str:
        qid = question_id or str(uuid.uuid4())
        with DatabaseEngine.instance().get_session() as session:
            session.add(
                QuestionORM(
                    id=qid,
                    domanda=domanda,
                    risposta_attesa=risposta_attesa,
                    categoria=categoria,
                )
            )
            session.commit()
        return qid

    @staticmethod
    def update(
        question_id: str,
        domanda: Optional[str] = None,
        risposta_attesa: Optional[str] = None,
        categoria: Optional[str] = None,
    ) -> bool:
        """Aggiorna una domanda esistente.

        Restituisce ``True`` se l'aggiornamento è andato a buon fine,
        ``False`` se la domanda non esiste.
        """
        with DatabaseEngine.instance().get_session() as session:
            q = session.get(QuestionORM, question_id)
            if not q:
                return False
            if domanda is not None:
                q.domanda = domanda
            if risposta_attesa is not None:
                q.risposta_attesa = risposta_attesa
            if categoria is not None:
                q.categoria = categoria
            session.commit()
            return True

    @staticmethod
    def delete(question_id: str) -> None:
        with DatabaseEngine.instance().get_session() as session:
            session.execute(
                delete(question_set_questions).where(question_set_questions.c.question_id == question_id)
            )
            q = session.get(QuestionORM, question_id)
            if q:
                session.delete(q)
            session.commit()

    @staticmethod
    def _persist_entities(df: pd.DataFrame) -> Tuple[int, List[str]]:
        """Persiste nuove domande da ``df`` evitando duplicati.

        Parametri
        ---------
        df: DataFrame
            Dati delle domande normalizzati.

        Restituisce
        -----------
        Tuple[int, list[str]]
            Numero di domande importate ed elenco degli avvisi.
        """

        warnings: List[str] = []
        with DatabaseEngine.instance().get_session() as session:
            existing_ids = session.execute(select(QuestionORM.id)).scalars().all()

            df_unique = df.drop_duplicates(subset="id", keep="first")
            duplicated_ids = set(df["id"].astype(str)) - set(
                df_unique["id"].astype(str)
            )
            for dup in duplicated_ids:
                warnings.append(
                    f"Domanda con ID '{dup}' già presente nel file; saltata."
                )

            new_rows, added_count = filter_new_rows(df_unique, existing_ids)
            skipped_ids = set(df_unique["id"].astype(str)) - set(
                new_rows["id"].astype(str)
            )
            for sid in skipped_ids:
                warnings.append(
                    f"Domanda con ID '{sid}' già esistente; saltata."
                )

            if added_count > 0:
                session.bulk_insert_mappings(
                    cast(Mapper[Any], QuestionORM.__mapper__),
                    new_rows.to_dict(orient="records"),
                )
                session.commit()

        return added_count, warnings

    @staticmethod
    def import_from_file(file: IO[str] | IO[bytes]) -> Dict[str, Any]:
        """Importa domande da un file CSV o JSON.

        Parametri
        ---------
        file: file-like
            File contenente le domande da importare.

        Restituisce
        -----------
        dict
            ``{"success": bool, "imported_count": int, "warnings": list[str]}``
        """

        try:
            df = read_questions(file)
        except ValueError as exc:
            return {"success": False, "imported_count": 0, "warnings": [str(exc)]}
        except Exception as exc:  # pragma: no cover - defensive
            return {
                "success": False,
                "imported_count": 0,
                "warnings": [f"Errore durante la lettura del file: {exc}"],
            }

        imported, warnings = Question._persist_entities(df)

        return {"success": True, "imported_count": imported, "warnings": warnings}

    @staticmethod
    def filter_by_category(
        category: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, List[str]]:
        """Restituisce le domande filtrate per categoria e tutte le categorie."""

        from utils.cache import get_questions  # Import locale per evitare cicli
        df = get_questions()
        df, _, categories = format_questions_for_view(df)
        filtered_df = df[df["categoria"] == category] if category else df

        return filtered_df, categories
