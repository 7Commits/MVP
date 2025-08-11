import logging

from dataclasses import dataclass, asdict
import uuid
from typing import Any, Dict, List, Tuple, cast
from functools import lru_cache

import pandas as pd
from sqlalchemy import select

from models.database import DatabaseEngine
from models.orm_models import TestResultORM
from utils.file_reader_utils import read_test_results, filter_new_rows
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    id: str
    set_id: str
    timestamp: str
    results: dict[str, Any]
    __test__ = False

    @staticmethod
    def load_all() -> List["TestResult"]:
        with DatabaseEngine.instance().get_session() as session:
            results = session.execute(select(TestResultORM)).scalars().all()
            return [
                TestResult(
                    id=cast(str, r.id),
                    set_id=cast(str, r.set_id),
                    timestamp=cast(str, r.timestamp),
                    results=cast(dict[str, Any], r.results or {}),
                )
                for r in results
            ]

    @staticmethod
    @lru_cache(maxsize=1)
    def load_all_df() -> pd.DataFrame:
        """Restituisce tutti i risultati come DataFrame pandas con caching."""
        data = [asdict(r) for r in TestResult.load_all()]
        columns = ["id", "set_id", "timestamp", "results"]
        return pd.DataFrame(data, columns=columns)

    @staticmethod
    def refresh_cache() -> pd.DataFrame:
        """Svuota e ricarica il DataFrame in cache dei risultati."""
        TestResult.load_all_df.cache_clear()
        return TestResult.load_all_df()

    @staticmethod
    def _persist_entities(imported_df: pd.DataFrame) -> int:
        """Persiste nuovi risultati di test evitando duplicati.

        Parametri
        ---------
        imported_df: DataFrame
            Dati dei risultati normalizzati.

        Restituisce
        -----------
        int
            Numero di nuovi risultati inseriti.
        """

        existing_df = TestResult.load_all_df()
        existing_ids = (
            existing_df["id"].astype(str).tolist() if not existing_df.empty else []
        )
        new_rows, added_count = filter_new_rows(imported_df, existing_ids)

        if added_count > 0:
            combined_df = pd.concat([existing_df, new_rows], ignore_index=True)
            results = [
                TestResult(**row) for row in combined_df.to_dict(orient="records")
            ]
            TestResult.save(results)
            TestResult.refresh_cache()
        return added_count

    @staticmethod
    def import_from_file(file) -> Tuple[bool, str]:
        """Importa risultati di test da ``file``.

        Il file è analizzato tramite :func:`utils.file_reader_utils.read_test_results`.
        I risultati esistenti (corrispondenti per ``id``) vengono ignorati. Le nuove
        voci vengono salvate e la cache viene aggiornata.
        """

        try:
            imported_df = read_test_results(file)
            added_count = TestResult._persist_entities(imported_df)
            message = (
                f"Importati {added_count} risultati."
                if added_count > 0
                else "Nessun nuovo risultato importato."
            )
            return True, message
        except ValueError as e:
            return False, str(e)
        except Exception as e:  # pragma: no cover
            return False, f"Errore durante l'importazione dei risultati: {str(e)}"

    @staticmethod
    def save(results: List["TestResult"]) -> None:
        """Salva un elenco di risultati di test."""
        with DatabaseEngine.instance().get_session() as session:
            existing_ids = session.execute(select(TestResultORM.id)).scalars().all()
            incoming_ids = [r.id for r in results]

            for rid in set(existing_ids) - set(incoming_ids):
                obj = session.get(TestResultORM, rid)
                if obj:
                    session.delete(obj)

            for result in results:
                obj = session.get(TestResultORM, result.id)
                if obj:
                    obj_cast = cast(Any, obj)
                    obj_cast.set_id = result.set_id
                    obj_cast.timestamp = result.timestamp
                    obj_cast.results = result.results
                else:
                    session.add(TestResultORM(**asdict(result)))
            session.commit()

    @staticmethod
    def add(set_id: str, results_data: dict[str, Any]) -> str:
        result_id = str(uuid.uuid4())
        with DatabaseEngine.instance().get_session() as session:
            session.add(
                TestResultORM(
                    id=result_id,
                    set_id=set_id,
                    timestamp=results_data.get('timestamp', ''),
                    results=results_data,
                )
            )
            session.commit()
        return result_id

    @staticmethod
    def add_and_refresh(set_id: str, results_data: dict[str, Any]) -> str:
        """Salva un singolo risultato e aggiorna il DataFrame in cache."""
        rid = TestResult.add(set_id, results_data)
        TestResult.refresh_cache()
        return rid

    @staticmethod
    def calculate_statistics(
        questions_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not questions_results:
            return {
                "avg_score": 0,
                "per_question_scores": [],
                "radar_metrics": {
                    "similarity": 0,
                    "correctness": 0,
                    "completeness": 0,
                },
            }

        per_question_scores: List[Dict[str, Any]] = []
        radar_sums = {"similarity": 0, "correctness": 0, "completeness": 0}

        for qdata in questions_results.values():
            evaluation = qdata.get("evaluation", {})
            score = evaluation.get("score", 0)
            per_question_scores.append(
                {"question": qdata.get("question", "Domanda"), "score": score}
            )
            for metric in radar_sums.keys():
                radar_sums[metric] += evaluation.get(metric, 0)

        count = len(per_question_scores)
        avg_score = (
            sum(item["score"] for item in per_question_scores) / count if count > 0 else 0
        )
        radar_metrics = {
            metric: radar_sums[metric] / count if count > 0 else 0
            for metric in radar_sums
        }
        return {
            "avg_score": avg_score,
            "per_question_scores": per_question_scores,
            "radar_metrics": radar_metrics,
        }

