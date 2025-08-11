import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import startup_controller as controller  # noqa: E402


def test_get_initial_state(monkeypatch):
    calls = []

    def mock_initialize_database():
        calls.append("init")

    def mock_load_default_config():
        calls.append("defaults")
        return {"conf": "value"}

    def mock_get_questions():
        calls.append("questions")
        return ["q1"]

    def mock_get_question_sets():
        calls.append("question_sets")
        return ["qs1"]

    def mock_get_results():
        calls.append("results")
        return ["r1"]

    monkeypatch.setattr(controller, "initialize_database", mock_initialize_database)
    monkeypatch.setattr(controller, "load_default_config", mock_load_default_config)
    monkeypatch.setattr(controller, "get_questions", mock_get_questions)
    monkeypatch.setattr(controller, "get_question_sets", mock_get_question_sets)
    monkeypatch.setattr(controller, "get_results", mock_get_results)

    state = controller.get_initial_state()

    assert state == {
        "questions": ["q1"],
        "question_sets": ["qs1"],
        "results": ["r1"],
        "conf": "value",
    }

    assert calls == [
        "init",
        "defaults",
        "questions",
        "question_sets",
        "results",
    ]
