import os
import sys
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.question import Question


class DummySession:
    def __init__(self):
        self.inserted = []

    def execute(self, *_args, **_kwargs):
        class Result:
            def scalars(self_inner):
                class Scal:
                    def all(self_inner2):
                        return ["q1"]
                return Scal()
        return Result()

    def bulk_insert_mappings(self, _orm, data):
        self.inserted.extend(data)

    def commit(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


class DummyEngine:
    def __init__(self):
        self.session = DummySession()

    def get_session(self):
        return self.session


@patch("models.question.DatabaseEngine.instance")
def test_import_from_file_skips_duplicates_and_adds_new(mock_engine):
    engine = DummyEngine()
    mock_engine.return_value = engine
    data_dir = os.path.join(os.path.dirname(__file__), "sample_data")

    for filename in ["questions.csv", "questions.json"]:
        engine.session.inserted.clear()
        with open(os.path.join(data_dir, filename), "r", encoding="utf-8") as f:
            result = Question.import_from_file(f)
        assert result["success"] is True
        assert result["imported_count"] == 1
        assert any("q1" in w for w in result["warnings"])
        assert engine.session.inserted == [
            {
                "id": "q2",
                "domanda": "New question?",
                "risposta_attesa": "Answer2",
                "categoria": "cat2",
            }
        ]

