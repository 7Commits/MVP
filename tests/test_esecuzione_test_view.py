import pytest

import importlib
import os
import sys
import pandas as pd
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def esecuzione_test(monkeypatch):
    import controllers
    import importlib.util
    from pathlib import Path

    monkeypatch.setattr(
        controllers,
        "load_presets",
        lambda: pd.DataFrame([{"name": "p"}]),
    )
    monkeypatch.setattr(
        controllers,
        "load_sets",
        lambda: pd.DataFrame([{"id": 1, "name": "s", "questions": [1]}]),
    )

    import streamlit as st

    class StopRender(Exception):
        pass

    monkeypatch.setattr(st, "stop", lambda: (_ for _ in ()).throw(StopRender()))

    base_path = Path(__file__).resolve().parents[1] / "views"
    style_spec = importlib.util.spec_from_file_location("views.style_utils", base_path / "style_utils.py")
    style_mod = importlib.util.module_from_spec(style_spec)
    sys.modules["views.style_utils"] = style_mod
    style_spec.loader.exec_module(style_mod)

    module_path = base_path / "esecuzione_test.py"
    spec = importlib.util.spec_from_file_location("views.esecuzione_test", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["views.esecuzione_test"] = module
    try:
        spec.loader.exec_module(module)
    except StopRender:
        pass
    return module


class DummySessionState(dict):
    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value


class DummySt:
    def __init__(self):
        self.session_state = DummySessionState()


def test_set_llm_mode_callback(monkeypatch, esecuzione_test):
    dummy_st = DummySt()
    dummy_st.session_state.test_mode = "Manual"
    dummy_st.session_state.mode_changed = False
    monkeypatch.setattr(esecuzione_test, "st", dummy_st)

    esecuzione_test.set_llm_mode_callback()

    assert dummy_st.session_state.test_mode == "Valutazione Automatica con LLM"
    assert dummy_st.session_state.mode_changed is True


def test_run_llm_test_callback(monkeypatch, esecuzione_test):
    dummy_st = DummySt()
    dummy_st.session_state.run_llm_test = False
    monkeypatch.setattr(esecuzione_test, "st", dummy_st)

    esecuzione_test.run_llm_test_callback()

    assert dummy_st.session_state.run_llm_test is True
