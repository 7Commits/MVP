import pytest

from views import session_state as ss


def test_initialize_session_state_writes_required_keys(monkeypatch):
    fake_defaults = {
        "questions": [],
        "question_sets": [],
        "results": [],
        "api_key": "key",
        "endpoint": "https://example.com",
        "model": "gpt-4",
        "temperature": 0.5,
        "max_tokens": 1000,
    }
    monkeypatch.setattr(ss, "get_initial_state", lambda: fake_defaults)
    monkeypatch.setattr(ss.st, "session_state", {})
    ss.initialize_session_state()
    for key, value in fake_defaults.items():
        assert ss.st.session_state[key] == value


def test_ensure_keys_respects_existing(monkeypatch):
    monkeypatch.setattr(ss.st, "session_state", {"existing": 1})
    ss.ensure_keys({"existing": 2, "missing": 3})
    assert ss.st.session_state["existing"] == 1
    assert ss.st.session_state["missing"] == 3
