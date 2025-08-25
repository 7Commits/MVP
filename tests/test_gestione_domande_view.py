import os
import sys
import importlib
import pandas as pd
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from views.state_models import QuestionPageState


@pytest.fixture
def gestione_domande(monkeypatch):
    import controllers
    import importlib.util
    from pathlib import Path

    monkeypatch.setattr(controllers, "load_questions", lambda: pd.DataFrame())

    base_path = Path(__file__).resolve().parents[1] / "views"
    style_spec = importlib.util.spec_from_file_location("views.style_utils", base_path / "style_utils.py")
    style_mod = importlib.util.module_from_spec(style_spec)
    sys.modules["views.style_utils"] = style_mod
    style_spec.loader.exec_module(style_mod)

    module_path = base_path / "gestione_domande.py"
    spec = importlib.util.spec_from_file_location("views.gestione_domande", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["views.gestione_domande"] = module
    spec.loader.exec_module(module)
    return module


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

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def success(self, *args, **kwargs):
        pass

    def button(self, *args, **kwargs):
        if self.button_returns:
            return self.button_returns.pop(0)
        return False

    def columns(self, n):
        return (DummyContext(), DummyContext())

    def rerun(self):
        self.rerun_called = True


def _setup(monkeypatch, gestione_domande):
    dummy_st = DummySt()
    monkeypatch.setattr(gestione_domande, "st", dummy_st)
    return dummy_st


def test_create_save_question_callback_success(monkeypatch, gestione_domande):
    dummy_st = _setup(monkeypatch, gestione_domande)
    questions_df = pd.DataFrame({"id": [1]})

    def fake_save_question_action(*_args):
        return {"success": True, "questions_df": questions_df}

    monkeypatch.setattr(
        gestione_domande, "save_question_action", fake_save_question_action
    )

    cb = gestione_domande.create_save_question_callback("1", "q", "a", "cat")
    cb()

    state: QuestionPageState = dummy_st.session_state.question_page_state
    assert state.save_success is True
    assert state.save_success_message == "Domanda salvata."
    assert state.trigger_rerun is True
    assert isinstance(dummy_st.session_state.questions, pd.DataFrame)


def test_create_save_question_callback_failure(monkeypatch, gestione_domande):
    dummy_st = _setup(monkeypatch, gestione_domande)

    def fake_save_question_action(*_args):
        return {"success": False}

    monkeypatch.setattr(
        gestione_domande, "save_question_action", fake_save_question_action
    )

    cb = gestione_domande.create_save_question_callback("1", "q", "a", "cat")
    cb()

    state: QuestionPageState = dummy_st.session_state.question_page_state
    assert state.save_error is True
    assert state.save_error_message == "Domanda non salvata."
    assert state.trigger_rerun is False


def test_import_questions_callback_success(monkeypatch, gestione_domande):
    dummy_st = _setup(monkeypatch, gestione_domande)
    dummy_st.session_state.uploaded_file_content = object()
    questions_df = pd.DataFrame({"id": [1]})

    def fake_import_questions_action(_file):
        return {"questions_df": questions_df, "imported_count": 2, "warnings": []}

    monkeypatch.setattr(
        gestione_domande, "import_questions_action", fake_import_questions_action
    )

    gestione_domande.import_questions_callback()

    state: QuestionPageState = dummy_st.session_state.question_page_state
    assert state.import_success is True
    assert "2" in state.import_success_message
    assert dummy_st.session_state.upload_questions_file is None
    assert "upload_questions_file" not in dummy_st.session_state
    assert isinstance(dummy_st.session_state.questions, pd.DataFrame)


def test_import_questions_callback_error(monkeypatch, gestione_domande):
    dummy_st = _setup(monkeypatch, gestione_domande)
    dummy_st.session_state.uploaded_file_content = object()

    def fake_import_questions_action(_file):
        raise Exception("bad")

    monkeypatch.setattr(
        gestione_domande, "import_questions_action", fake_import_questions_action
    )

    gestione_domande.import_questions_callback()

    state: QuestionPageState = dummy_st.session_state.question_page_state
    assert state.import_error is True
    assert state.import_error_message == "bad"
    assert "upload_questions_file" not in dummy_st.session_state
    assert dummy_st.session_state.uploaded_file_content is None


def test_confirm_delete_question_dialog_success(monkeypatch, gestione_domande):
    dummy_st = _setup(monkeypatch, gestione_domande)
    dummy_st.button_returns = [True, False]
    questions_df = pd.DataFrame({"id": [1]})

    def fake_delete_question_action(_id):
        return questions_df

    monkeypatch.setattr(
        gestione_domande, "delete_question_action", fake_delete_question_action
    )

    gestione_domande.confirm_delete_question_dialog.__wrapped__(1, "q1")

    state: QuestionPageState = dummy_st.session_state.question_page_state
    assert state.delete_success is True
    assert state.trigger_rerun is True
    assert dummy_st.rerun_called is True
    assert isinstance(dummy_st.session_state.questions, pd.DataFrame)


def test_confirm_delete_question_dialog_error(monkeypatch, gestione_domande):
    dummy_st = _setup(monkeypatch, gestione_domande)
    dummy_st.button_returns = [True, False]

    def fake_delete_question_action(_id):
        raise Exception("fail")

    monkeypatch.setattr(
        gestione_domande, "delete_question_action", fake_delete_question_action
    )

    gestione_domande.confirm_delete_question_dialog.__wrapped__(1, "q1")

    state: QuestionPageState = dummy_st.session_state.question_page_state
    assert state.save_error is True
    assert state.save_error_message == "fail"
    assert dummy_st.rerun_called is True

