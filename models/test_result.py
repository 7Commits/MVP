from dataclasses import dataclass
from typing import Dict, Optional
import uuid
import json
import pandas as pd
from sqlalchemy import text

from models.db_utils import get_engine

@dataclass
class TestResult:
    id: str
    set_id: str
    timestamp: str
    results: Dict

    @staticmethod
    def load_all() -> pd.DataFrame:
        df = pd.read_sql("SELECT * FROM test_results", get_engine())
        if 'results' in df.columns:
            df['results'] = df['results'].apply(lambda x: json.loads(x) if isinstance(x, str) else {})
        df['id'] = df['id'].astype(str)
        return df

    @staticmethod
    def save_df(df: pd.DataFrame) -> None:
        df_to_save = df.copy()
        if 'results' in df_to_save.columns:
            df_to_save['results'] = df_to_save['results'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else '{}')
        engine = get_engine()
        with engine.begin() as conn:
            existing_ids = pd.read_sql('SELECT id FROM test_results', conn)['id'].astype(str).tolist()
            incoming_ids = df_to_save['id'].astype(str).tolist()
            for rid in set(existing_ids) - set(incoming_ids):
                conn.execute(text('DELETE FROM test_results WHERE id=:id'), {'id': rid})
            for _, row in df_to_save.iterrows():
                params = row.to_dict()
                if row['id'] in existing_ids:
                    conn.execute(text('''UPDATE test_results SET set_id=:set_id, timestamp=:timestamp, results=:results WHERE id=:id'''), params)
                else:
                    conn.execute(text('''INSERT INTO test_results (id, set_id, timestamp, results) VALUES (:id, :set_id, :timestamp, :results)'''), params)

    @staticmethod
    def add(set_id: str, results_data: Dict) -> str:
        result_id = str(uuid.uuid4())
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(
                text('INSERT INTO test_results (id, set_id, timestamp, results) VALUES (:id, :set_id, :timestamp, :results)'),
                {
                    'id': result_id,
                    'set_id': set_id,
                    'timestamp': results_data.get('timestamp', ''),
                    'results': json.dumps(results_data)
                }
            )
        return result_id
