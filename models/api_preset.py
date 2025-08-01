from dataclasses import dataclass
from typing import Optional
import pandas as pd
from sqlalchemy import text

from models.db_utils import get_engine

@dataclass
class APIPreset:
    id: str
    name: str
    provider_name: str
    endpoint: str
    api_key: str
    model: str
    temperature: float
    max_tokens: int

    @staticmethod
    def load_all() -> pd.DataFrame:
        df = pd.read_sql("SELECT * FROM api_presets", get_engine())
        df['id'] = df['id'].astype(str)
        return df

    @staticmethod
    def save_df(df: pd.DataFrame) -> None:
        engine = get_engine()
        with engine.begin() as conn:
            existing_ids = pd.read_sql('SELECT id FROM api_presets', conn)['id'].astype(str).tolist()
            incoming_ids = df['id'].astype(str).tolist()
            for del_id in set(existing_ids) - set(incoming_ids):
                conn.execute(text('DELETE FROM api_presets WHERE id=:id'), {'id': del_id})
            for _, row in df.iterrows():
                # Convert NaN values from Pandas to None so that SQLAlchemy can
                # correctly insert NULLs into the database instead of the string
                # "nan" which would raise a ProgrammingError with MySQL.
                params = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
                if row['id'] in existing_ids:
                    conn.execute(text('''UPDATE api_presets SET name=:name, provider_name=:provider_name, endpoint=:endpoint, api_key=:api_key, model=:model, temperature=:temperature, max_tokens=:max_tokens WHERE id=:id'''), params)
                else:
                    conn.execute(text('''INSERT INTO api_presets (id, name, provider_name, endpoint, api_key, model, temperature, max_tokens) VALUES (:id, :name, :provider_name, :endpoint, :api_key, :model, :temperature, :max_tokens)'''), params)

    @staticmethod
    def delete(preset_id: str) -> None:
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(text('DELETE FROM api_presets WHERE id=:id'), {'id': preset_id})
