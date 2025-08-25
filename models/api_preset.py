import logging

from dataclasses import dataclass, asdict
from typing import List
from sqlalchemy import select

from models.database import DatabaseEngine
from models.orm_models import APIPresetORM
logger = logging.getLogger(__name__)


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
        with DatabaseEngine.instance().get_session() as session:
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
    def save(presets: List["APIPreset"]) -> None:
        """Salva un elenco di preset API."""
        with DatabaseEngine.instance().get_session() as session:
            existing_ids = session.execute(select(APIPresetORM.id)).scalars().all()
            incoming_ids = [p.id for p in presets]

            for del_id in set(existing_ids) - set(incoming_ids):
                obj = session.get(APIPresetORM, del_id)
                if obj:
                    session.delete(obj)

            for preset in presets:
                obj = session.get(APIPresetORM, preset.id)
                if obj:
                    obj.name = preset.name
                    obj.provider_name = preset.provider_name
                    obj.endpoint = preset.endpoint
                    obj.api_key = preset.api_key
                    obj.model = preset.model
                    obj.temperature = preset.temperature
                    obj.max_tokens = preset.max_tokens
                else:
                    session.add(APIPresetORM(**asdict(preset)))
            session.commit()

    @staticmethod
    def delete(preset_id: str) -> None:
        with DatabaseEngine.instance().get_session() as session:
            obj = session.get(APIPresetORM, preset_id)
            if obj:
                session.delete(obj)
            session.commit()
