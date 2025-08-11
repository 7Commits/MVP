import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from views.state_models import SetPageState
from models.question_set import PersistSetsResult


class DummySessionState(dict):
    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value


class DummySt:
    def __init__(self):
        self.session_state = DummySessionState()
        self.captured_warnings: list[str] = []

    def warning(self, msg):
        self.captured_warnings.append(msg)


def _setup(monkeypatch):
    from views import set_helpers

    dummy_st = DummySt()
    monkeypatch.setattr(set_helpers, "st", dummy_st)
    return set_helpers, dummy_st


def test_save_set_callback_success(monkeypatch):
    set_helpers, dummy_st = _setup(monkeypatch)

    sets_df = pd.DataFrame({"id": [1]})

    def fake_update_set(_set_id, _name, _ids):
        return sets_df, "ok"

    monkeypatch.setattr(set_helpers, "update_set", fake_update_set)

    state = SetPageState()
    set_helpers.save_set_callback("1", "name", {}, [], state)

    assert state.save_set_success is True
    assert state.save_set_success_message == "ok"
    assert isinstance(dummy_st.session_state.question_sets, pd.DataFrame)


def test_save_set_callback_error(monkeypatch):
    set_helpers, dummy_st = _setup(monkeypatch)

    def fake_update_set(*_args, **_kwargs):
        raise Exception("boom")

    monkeypatch.setattr(set_helpers, "update_set", fake_update_set)

    state = SetPageState()
    set_helpers.save_set_callback("1", "name", {}, [], state)

    assert state.save_set_error is True
    assert state.save_set_error_message == "boom"
    assert "question_sets" not in dummy_st.session_state


def test_delete_set_callback_success(monkeypatch):
    set_helpers, dummy_st = _setup(monkeypatch)

    sets_df = pd.DataFrame({"id": [1]})

    def fake_delete_set(_set_id):
        return sets_df, "deleted"

    monkeypatch.setattr(set_helpers, "delete_set", fake_delete_set)

    state = SetPageState()
    set_helpers.delete_set_callback("1", state)

    assert state.delete_set_success is True
    assert state.delete_set_success_message == "deleted"
    assert isinstance(dummy_st.session_state.question_sets, pd.DataFrame)


def test_delete_set_callback_error(monkeypatch):
    set_helpers, dummy_st = _setup(monkeypatch)

    def fake_delete_set(_set_id):
        raise Exception("fail")

    monkeypatch.setattr(set_helpers, "delete_set", fake_delete_set)

    state = SetPageState()
    set_helpers.delete_set_callback("1", state)

    assert state.save_set_error is True
    assert state.save_set_error_message == "fail"
    assert "question_sets" not in dummy_st.session_state


def test_import_set_callback_success(monkeypatch):
    set_helpers, dummy_st = _setup(monkeypatch)
    dummy_st.session_state.uploaded_file_content_set = object()

    result = PersistSetsResult(
        sets_df=pd.DataFrame({"id": [1]}),
        questions_df=pd.DataFrame({"id": [2]}),
        sets_imported_count=1,
        new_questions_added_count=0,
        existing_questions_found_count=0,
        warnings=["warn"],
    )

    monkeypatch.setattr(set_helpers.QuestionSet, "import_from_file", lambda _f: result)

    state = SetPageState()
    set_helpers.import_set_callback(state)

    assert state.import_set_success is True
    assert state.import_set_success_message == "1 set importati."
    assert isinstance(dummy_st.session_state.question_sets, pd.DataFrame)
    assert isinstance(dummy_st.session_state.questions, pd.DataFrame)
    assert dummy_st.captured_warnings == ["warn"]
    assert dummy_st.session_state.uploaded_file_content_set is None


def test_import_set_callback_error(monkeypatch):
    set_helpers, dummy_st = _setup(monkeypatch)
    dummy_st.session_state.uploaded_file_content_set = object()
    dummy_st.session_state.upload_set_file = object()

    def fake_import_from_file(_f):
        raise Exception("bad")

    monkeypatch.setattr(set_helpers.QuestionSet, "import_from_file", fake_import_from_file)

    state = SetPageState()
    set_helpers.import_set_callback(state)

    assert state.import_set_error is True
    assert state.import_set_error_message == "bad"
    assert dummy_st.session_state.uploaded_file_content_set is None
    assert "upload_set_file" not in dummy_st.session_state

