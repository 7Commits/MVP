import os
import sys
import importlib
import pandas as pd
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def visualizza_risultati(monkeypatch):
    import controllers
    import importlib.util
    import json
    from pathlib import Path

    monkeypatch.setattr(
        controllers,
        "get_results",
        lambda *_a, **_k: pd.DataFrame(
            [{"id": 1, "set_id": 1, "timestamp": "t", "results": {}}]
        ),
    )
    monkeypatch.setattr(
        controllers, "load_sets", lambda: pd.DataFrame([{ "id": 1, "name": "s" }])
    )
    monkeypatch.setattr(controllers, "list_set_names", lambda *_a: ["s"])
    monkeypatch.setattr(controllers, "list_model_names", lambda *_a: ["m"])
    monkeypatch.setattr(
        controllers, "prepare_select_options", lambda df, sets: {1: "r"}
    )
    monkeypatch.setattr(json, "dumps", lambda *a, **k: "{}")

    base_path = Path(__file__).resolve().parents[1] / "views"
    style_spec = importlib.util.spec_from_file_location("views.style_utils", base_path / "style_utils.py")
    style_mod = importlib.util.module_from_spec(style_spec)
    sys.modules["views.style_utils"] = style_mod
    style_spec.loader.exec_module(style_mod)

    module_path = base_path / "visualizza_risultati.py"
    spec = importlib.util.spec_from_file_location("views.visualizza_risultati", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["views.visualizza_risultati"] = module
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
        self.captured_callbacks = {}

    def success(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def write(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def markdown(self, *args, **kwargs):
        pass

    def selectbox(self, label, options, index=0, **kwargs):
        return options[index]

    def text_input(self, label, value="", **kwargs):
        return value

    def button(self, label, on_click=None, **kwargs):
        if on_click:
            self.captured_callbacks[label] = on_click
        return False

    def file_uploader(self, *args, **kwargs):
        return None

    def download_button(self, *args, **kwargs):
        pass

    def expander(self, *args, **kwargs):
        return DummyContext()

    def columns(self, n):
        return (DummyContext(), DummyContext())

    def stop(self):
        pass


class StopRender(Exception):
    pass


def _setup(monkeypatch, visualizza_risultati):
    dummy_st = DummySt()
    monkeypatch.setattr(visualizza_risultati, "st", dummy_st)
    monkeypatch.setattr(visualizza_risultati, "add_page_header", lambda *a, **k: None)
    monkeypatch.setattr(visualizza_risultati.json, "dumps", lambda *a, **k: "{}")

    res_df = pd.DataFrame([
        {"id": 1, "set_id": 1, "timestamp": "t", "results": {"method": "LLM"}}
    ])
    sets_df = pd.DataFrame([{"id": 1, "name": "s"}])

    monkeypatch.setattr(visualizza_risultati, "get_results", lambda *_a, **_k: res_df)
    monkeypatch.setattr(visualizza_risultati, "load_sets", lambda: sets_df)
    monkeypatch.setattr(visualizza_risultati, "list_set_names", lambda *_a: ["s"])
    monkeypatch.setattr(visualizza_risultati, "list_model_names", lambda *_a: ["m"])
    monkeypatch.setattr(
        visualizza_risultati, "prepare_select_options", lambda df, sets: {1: "r"}
    )

    def fake_add_section_title(*args, **kwargs):
        raise StopRender()

    monkeypatch.setattr(visualizza_risultati, "add_section_title", fake_add_section_title)

    try:
        visualizza_risultati.render()
    except StopRender:
        pass

    return dummy_st


def test_import_results_callback_success(monkeypatch, visualizza_risultati):
    dummy_st = _setup(monkeypatch, visualizza_risultati)
    callback = dummy_st.captured_callbacks.get("Importa Risultati")
    assert callback is not None

    res_df = pd.DataFrame([{"id": 2, "set_id": 1, "timestamp": "t2", "results": {}}])

    def fake_import_results_action(_file):
        return res_df, "ok"

    monkeypatch.setattr(visualizza_risultati, "import_results_action", fake_import_results_action)

    dummy_st.session_state.uploaded_results_file = object()
    callback()

    assert dummy_st.session_state.import_results_success is True
    assert dummy_st.session_state.import_results_message == "ok"
    assert dummy_st.session_state.import_results_error is False
    assert dummy_st.session_state.uploaded_results_file is None
    assert dummy_st.session_state.upload_results is None
    assert isinstance(dummy_st.session_state.results, pd.DataFrame)


def test_import_results_callback_error(monkeypatch, visualizza_risultati):
    dummy_st = _setup(monkeypatch, visualizza_risultati)
    callback = dummy_st.captured_callbacks.get("Importa Risultati")
    assert callback is not None

    def fake_import_results_action(_file):
        raise Exception("fail")

    monkeypatch.setattr(visualizza_risultati, "import_results_action", fake_import_results_action)

    dummy_st.session_state.uploaded_results_file = object()
    callback()

    assert dummy_st.session_state.import_results_error is True
    assert dummy_st.session_state.import_results_message == "fail"
    assert dummy_st.session_state.import_results_success is False
    assert dummy_st.session_state.uploaded_results_file is None
    assert dummy_st.session_state.upload_results is None

