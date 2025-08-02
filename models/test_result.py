from dataclasses import dataclass
from typing import Dict
import uuid
import json
import pandas as pd
from sqlalchemy import select

from models.db_utils import get_session
from models.orm_models import TestResultORM


@dataclass
class TestResult:
    id: str
    set_id: str
    timestamp: str
    results: Dict

    @staticmethod
    def load_all() -> pd.DataFrame:
        with get_session() as session:
            results = session.execute(select(TestResultORM)).scalars().all()
            data = []
            for r in results:
                data.append({
                    "id": r.id,
                    "set_id": r.set_id,
                    "timestamp": r.timestamp,
                    "results": r.results or {},
                })
        columns = ["id", "set_id", "timestamp", "results"]
        return pd.DataFrame(data, columns=columns)

    @staticmethod
    def save_df(df: pd.DataFrame) -> None:
        df_to_save = df.copy()
        if 'results' in df_to_save.columns:
            df_to_save['results'] = df_to_save['results'].apply(
                lambda x: json.dumps(x) if isinstance(x, dict) else '{}'
            )
        with get_session() as session:
            existing_ids = session.execute(select(TestResultORM.id)).scalars().all()
            incoming_ids = df_to_save['id'].astype(str).tolist()
            for rid in set(existing_ids) - set(incoming_ids):
                obj = session.get(TestResultORM, rid)
                if obj:
                    session.delete(obj)
            for _, row in df_to_save.iterrows():
                params = row.to_dict()
                obj = session.get(TestResultORM, params['id'])
                if obj:
                    obj.set_id = params['set_id']
                    obj.timestamp = params['timestamp']
                    obj.results = json.loads(params['results'])
                else:
                    session.add(
                        TestResultORM(
                            id=params['id'],
                            set_id=params['set_id'],
                            timestamp=params['timestamp'],
                            results=json.loads(params['results']),
                        )
                    )
            session.commit()

    @staticmethod
    def add(set_id: str, results_data: Dict) -> str:
        result_id = str(uuid.uuid4())
        with get_session() as session:
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
