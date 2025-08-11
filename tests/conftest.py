import pathlib
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from models.database import DatabaseEngine, Base


@pytest.fixture()
def in_memory_db():
    # Reset singleton to ensure clean state
    DatabaseEngine._instance = None  # type: ignore[attr-defined]
    db = DatabaseEngine.instance()
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    db._engine = engine  # type: ignore[attr-defined]
    db._session_factory = sessionmaker(bind=engine)  # type: ignore[attr-defined]
    yield db
    # Reset after test
    DatabaseEngine._instance = None  # type: ignore[attr-defined]

