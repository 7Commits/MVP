from dataclasses import dataclass
from typing import List
import pandas as pd
from sqlalchemy import select

from models.db_utils import get_session
from models.orm_models import APIPresetORM


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
    def load_all() -> List["APIPreset"]:
        with get_session() as session:
            presets = session.execute(select(APIPresetORM)).scalars().all()
            return [
                APIPreset(
                    id=p.id,
                    name=p.name,
                    provider_name=p.provider_name,
                    endpoint=p.endpoint,
                    api_key=p.api_key,
                    model=p.model,
                    temperature=p.temperature,
                    max_tokens=p.max_tokens,
                )
                for p in presets
            ]

    @staticmethod
    def save_df(df: pd.DataFrame) -> None:
        with get_session() as session:
            existing_ids = session.execute(select(APIPresetORM.id)).scalars().all()
            incoming_ids = df['id'].astype(str).tolist()
            for del_id in set(existing_ids) - set(incoming_ids):
                obj = session.get(APIPresetORM, del_id)
                if obj:
                    session.delete(obj)
            for _, row in df.iterrows():
                params = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
                obj = session.get(APIPresetORM, params['id'])
                if obj:
                    obj.name = params['name']
                    obj.provider_name = params['provider_name']
                    obj.endpoint = params['endpoint']
                    obj.api_key = params['api_key']
                    obj.model = params['model']
                    obj.temperature = params['temperature']
                    obj.max_tokens = params['max_tokens']
                else:
                    session.add(APIPresetORM(**params))
            session.commit()

    @staticmethod
    def delete(preset_id: str) -> None:
        with get_session() as session:
            obj = session.get(APIPresetORM, preset_id)
            if obj:
                session.delete(obj)
            session.commit()
