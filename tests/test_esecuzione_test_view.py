import pytest

from views import esecuzione_test


class DummySessionState(dict):
    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value


class DummySt:
    def __init__(self):
        self.session_state = DummySessionState()


def test_set_llm_mode_callback(monkeypatch):
    dummy_st = DummySt()
    dummy_st.session_state.test_mode = "Manual"
    dummy_st.session_state.mode_changed = False
    monkeypatch.setattr(esecuzione_test, "st", dummy_st)

    esecuzione_test.set_llm_mode_callback()

    assert dummy_st.session_state.test_mode == "Valutazione Automatica con LLM"
    assert dummy_st.session_state.mode_changed is True


def test_run_llm_test_callback(monkeypatch):
    dummy_st = DummySt()
    dummy_st.session_state.run_llm_test = False
    monkeypatch.setattr(esecuzione_test, "st", dummy_st)

    esecuzione_test.run_llm_test_callback()

    assert dummy_st.session_state.run_llm_test is True
