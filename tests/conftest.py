import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from sqlalchemy import create_engine
from models import db_utils, question, question_set

@pytest.fixture(autouse=True)
def in_memory_db(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    # Patch get_engine in db_utils and imported references
    monkeypatch.setattr(db_utils, "_engine", engine)
    monkeypatch.setattr(db_utils, "get_engine", lambda: engine)
    monkeypatch.setattr(question, "get_engine", lambda: engine)
    monkeypatch.setattr(question_set, "get_engine", lambda: engine)
    db_utils.init_db()
    yield engine
    engine.dispose()
