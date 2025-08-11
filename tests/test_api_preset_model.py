import os
import sys
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import models.api_preset as api_preset_module
from models.api_preset import APIPreset
from models.orm_models import APIPresetORM
from models.database import Base


@pytest.fixture
def session_factory(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    dummy_engine = SimpleNamespace(get_session=lambda: SessionLocal())
    monkeypatch.setattr(api_preset_module.DatabaseEngine, "instance", lambda: dummy_engine)
    return SessionLocal


def test_load_all_returns_correct_attributes(session_factory):
    session = session_factory()
    session.add(
        APIPresetORM(
            id="1",
            name="Preset",
            provider_name="OpenAI",
            endpoint="http://api",
            api_key="key",
            model="gpt",
            temperature=0.7,
            max_tokens=1000,
        )
    )
    session.commit()
    session.close()

    presets = APIPreset.load_all()
    assert len(presets) == 1
    preset = presets[0]
    assert preset.id == "1"
    assert preset.name == "Preset"
    assert preset.provider_name == "OpenAI"
    assert preset.endpoint == "http://api"
    assert preset.api_key == "key"
    assert preset.model == "gpt"
    assert preset.temperature == 0.7
    assert preset.max_tokens == 1000


def test_save_inserts_and_updates(session_factory):
    APIPreset.save([
        APIPreset(
            id="1",
            name="Initial",
            provider_name="P",
            endpoint="E",
            api_key="K",
            model="M",
            temperature=0.1,
            max_tokens=50,
        )
    ])

    session = session_factory()
    row = session.get(APIPresetORM, "1")
    assert row.name == "Initial"
    assert row.max_tokens == 50
    session.close()

    APIPreset.save([
        APIPreset(
            id="1",
            name="Updated",
            provider_name="P2",
            endpoint="E2",
            api_key="K2",
            model="M2",
            temperature=0.2,
            max_tokens=150,
        )
    ])

    session = session_factory()
    row = session.get(APIPresetORM, "1")
    assert row.name == "Updated"
    assert row.provider_name == "P2"
    assert row.endpoint == "E2"
    assert row.api_key == "K2"
    assert row.model == "M2"
    assert row.temperature == 0.2
    assert row.max_tokens == 150
    session.close()


def test_delete_existing_and_non_existing(session_factory):
    session = session_factory()
    session.add(
        APIPresetORM(
            id="1",
            name="Preset",
            provider_name="P",
            endpoint="E",
            api_key="K",
            model="M",
            temperature=0.1,
            max_tokens=10,
        )
    )
    session.commit()
    session.close()

    APIPreset.delete("1")
    session = session_factory()
    assert session.get(APIPresetORM, "1") is None
    session.close()

    APIPreset.delete("nonexistent")
    session = session_factory()
    assert session.query(APIPresetORM).count() == 0
    session.close()
