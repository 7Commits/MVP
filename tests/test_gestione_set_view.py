import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from views import set_helpers
from views.state_models import SetPageState
from models.question_set import PersistSetsResult


class DummySessionState(dict):
    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value


class DummyContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class DummySt:
    def __init__(self):
        self.session_state = DummySessionState()
        self.button_returns: list[bool] = []
        self.rerun_called = False

    def write(self, *args, **kwargs):
        pass

    def button(self, *args, **kwargs):
        if self.button_returns:
            return self.button_returns.pop(0)
        return False

    def columns(self, n):
        return (DummyContext(), DummyContext())

    def warning(self, *args, **kwargs):
        pass

    def rerun(self):
        self.rerun_called = True


def _setup(monkeypatch):
    dummy_st = DummySt()
    monkeypatch.setattr(set_helpers, "st", dummy_st)
    return dummy_st


def test_create_save_set_callback_success(monkeypatch):
    dummy_st = _setup(monkeypatch)
    dummy_st.session_state.set_expanders = {}
    dummy_st.session_state.question_checkboxes = {"1": {"2": True}}
    dummy_st.session_state.newly_selected_questions = {"1": ["3"]}
    dummy_st.session_state.set_name_1 = "Name"
    state = SetPageState()

    captured = {}

    def fake_save_set_callback(set_id, name, options, new_ids, st_state):
        captured["args"] = (set_id, name, options, new_ids)
        st_state.save_set_success = True

    monkeypatch.setattr(set_helpers, "save_set_callback", fake_save_set_callback)

    cb = set_helpers.create_save_set_callback("1", "exp1", state)
    cb()

    assert dummy_st.session_state.set_expanders["exp1"] is True
    assert captured["args"] == (
        "1",
        "Name",
        {"2": True},
        ["3"],
    )
    assert state.save_set_success is True


def test_create_save_set_callback_error(monkeypatch):
    dummy_st = _setup(monkeypatch)
    dummy_st.session_state.set_expanders = {}
    dummy_st.session_state.question_checkboxes = {"1": {}}
    dummy_st.session_state.newly_selected_questions = {"1": []}
    dummy_st.session_state.set_name_1 = "Name"
    state = SetPageState()

    def fake_save_set_callback(set_id, name, options, new_ids, st_state):
        st_state.save_set_error = True
        st_state.save_set_error_message = "boom"

    monkeypatch.setattr(set_helpers, "save_set_callback", fake_save_set_callback)

    cb = set_helpers.create_save_set_callback("1", "exp1", state)
    cb()

    assert dummy_st.session_state.set_expanders["exp1"] is True
    assert state.save_set_error is True
    assert state.save_set_error_message == "boom"


def test_import_set_callback_success(monkeypatch):
    dummy_st = _setup(monkeypatch)
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
    assert dummy_st.session_state.uploaded_file_content_set is None


def test_import_set_callback_error(monkeypatch):
    dummy_st = _setup(monkeypatch)
    dummy_st.session_state.uploaded_file_content_set = object()
    dummy_st.session_state.upload_set_file = object()

    def fake_import_from_file(_f):
        raise Exception("fail")

    monkeypatch.setattr(set_helpers.QuestionSet, "import_from_file", fake_import_from_file)

    state = SetPageState()
    set_helpers.import_set_callback(state)

    assert state.import_set_error is True
    assert state.import_set_error_message == "fail"
    assert dummy_st.session_state.uploaded_file_content_set is None
    assert "upload_set_file" not in dummy_st.session_state


def test_confirm_delete_set_dialog_success(monkeypatch):
    dummy_st = _setup(monkeypatch)
    dummy_st.button_returns = [True, False]
    state = SetPageState()

    def fake_delete_set_callback(set_id, st_state):
        st_state.delete_set_success = True
        dummy_st.session_state.question_sets = pd.DataFrame({"id": [1]})

    monkeypatch.setattr(set_helpers, "delete_set_callback", fake_delete_set_callback)

    set_helpers.confirm_delete_set_dialog.__wrapped__("1", "name", state)

    assert state.delete_set_success is True
    assert isinstance(dummy_st.session_state.question_sets, pd.DataFrame)
    assert dummy_st.rerun_called is True


def test_confirm_delete_set_dialog_error(monkeypatch):
    dummy_st = _setup(monkeypatch)
    dummy_st.button_returns = [True, False]
    state = SetPageState()

    def fake_delete_set_callback(set_id, st_state):
        st_state.save_set_error = True
        st_state.save_set_error_message = "bad"

    monkeypatch.setattr(set_helpers, "delete_set_callback", fake_delete_set_callback)

    set_helpers.confirm_delete_set_dialog.__wrapped__("1", "name", state)

    assert state.save_set_error is True
    assert state.save_set_error_message == "bad"
    assert dummy_st.rerun_called is True

