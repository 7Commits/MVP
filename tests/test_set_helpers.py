import pandas as pd

from views.state_models import SetPageState
from models.question_set import PersistSetsResult

# create dummy st object

class DummySessionState(dict):
    def __getattr__(self, name):
        return self.get(name)
    def __setattr__(self, name, value):
        self[name] = value

class DummySt:
    def __init__(self):
        self.session_state = DummySessionState()
        self.captured_warnings = []
    def warning(self, msg):
        self.captured_warnings.append(msg)


def test_import_set_callback_message_and_warnings(monkeypatch):
    from views import set_helpers

    dummy_st = DummySt()
    dummy_st.session_state.uploaded_file_content_set = object()
    monkeypatch.setattr(set_helpers, "st", dummy_st)

    result = PersistSetsResult(
        sets_df=pd.DataFrame(),
        questions_df=pd.DataFrame(),
        sets_imported_count=2,
        new_questions_added_count=1,
        existing_questions_found_count=0,
        warnings=["w1", "w2"],
    )
    monkeypatch.setattr(set_helpers.QuestionSet, "import_from_file", lambda _: result)

    state = SetPageState()
    set_helpers.import_set_callback(state)

    assert state.import_set_success is True
    assert state.import_set_success_message == "2 set importati. 1 nuove domande aggiunte."
    assert dummy_st.captured_warnings == ["w1", "w2"]
    assert isinstance(dummy_st.session_state.questions, pd.DataFrame)
    assert isinstance(dummy_st.session_state.question_sets, pd.DataFrame)
    assert dummy_st.session_state.uploaded_file_content_set is None


def test_import_set_callback_no_imports_with_warnings(monkeypatch):
    from views import set_helpers

    dummy_st = DummySt()
    dummy_st.session_state.uploaded_file_content_set = object()
    monkeypatch.setattr(set_helpers, "st", dummy_st)

    result = PersistSetsResult(
        sets_df=pd.DataFrame(),
        questions_df=pd.DataFrame(),
        sets_imported_count=0,
        new_questions_added_count=0,
        existing_questions_found_count=0,
        warnings=["warn"],
    )
    monkeypatch.setattr(set_helpers.QuestionSet, "import_from_file", lambda _: result)

    state = SetPageState()
    set_helpers.import_set_callback(state)

    assert state.import_set_success is True
    assert (
        state.import_set_success_message
        == "Nessun set importato. Controlla gli avvisi."
    )
    assert dummy_st.captured_warnings == ["warn"]
    assert dummy_st.session_state.uploaded_file_content_set is None
