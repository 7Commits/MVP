import pathlib
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from models.database import DatabaseEngine, Base


@pytest.fixture()
def in_memory_db():
    # Reimposta il singleton per garantire uno stato pulito
    DatabaseEngine.reset_instance()
    db = DatabaseEngine.instance()
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    db._engine = engine  # type: ignore[attr-defined]
    db._session_factory = sessionmaker(bind=engine)  # type: ignore[attr-defined]
    yield db
    # Reimposta dopo il test
    DatabaseEngine.reset_instance()

