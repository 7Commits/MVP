import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.openai_client import DEFAULT_MODEL, DEFAULT_ENDPOINT
from views import api_configurazione as view


class DummySessionState(dict):
    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value


class DummySt:
    def __init__(self):
        self.session_state = DummySessionState()
        self.errors = []
        self.successes = []

    def error(self, msg):
        self.errors.append(msg)

    def success(self, msg):
        self.successes.append(msg)


def test_start_new_preset_edit_initializes_session_state(monkeypatch):
    dummy = DummySt()
    monkeypatch.setattr(view, "st", dummy)

    view.start_new_preset_edit()

    assert dummy.session_state.editing_preset is True
    assert dummy.session_state.current_preset_edit_id is None
    assert dummy.session_state.preset_form_data == {
        "name": "",
        "endpoint": DEFAULT_ENDPOINT,
        "api_key": "",
        "model": DEFAULT_MODEL,
        "temperature": 0.0,
        "max_tokens": 1000,
    }


def test_start_existing_preset_edit_initializes_session_state(monkeypatch, mocker):
    dummy = DummySt()
    dummy.session_state.api_presets = object()
    monkeypatch.setattr(view, "st", dummy)

    preset = {
        "name": "Existing",
        "endpoint": "e",
        "api_key": "k",
        "model": "m",
        "temperature": "0.2",
        "max_tokens": "200",
    }
    mocker.patch("views.api_configurazione.get_preset_by_id", return_value=preset)
    view.start_existing_preset_edit("123")

    assert dummy.session_state.editing_preset is True
    assert dummy.session_state.current_preset_edit_id == "123"
    assert dummy.session_state.preset_form_data == {
        "name": "Existing",
        "endpoint": "e",
        "api_key": "k",
        "model": "m",
        "temperature": 0.2,
        "max_tokens": 200,
    }
    assert dummy.errors == []


def test_save_preset_from_form_validation_error(monkeypatch, mocker):
    dummy = DummySt()
    dummy.session_state.preset_form_data = {}
    dummy.session_state.current_preset_edit_id = None
    monkeypatch.setattr(view, "st", dummy)

    mocker.patch("views.api_configurazione.validate_preset", return_value=(False, "err"))
    mock_save = mocker.patch("views.api_configurazione.save_preset")
    view.save_preset_from_form()
    mock_save.assert_not_called()

    assert dummy.errors == ["err"]


def test_save_preset_from_form_success(monkeypatch, mocker):
    dummy = DummySt()
    dummy.session_state.update(
        {
            "preset_form_data": {},
            "current_preset_edit_id": "1",
            "editing_preset": True,
            "preset_name": "Name",
            "preset_endpoint": "e",
            "preset_api_key": "k",
            "preset_model": "m",
            "preset_temperature": 0.2,
            "preset_max_tokens": 200,
        }
    )
    monkeypatch.setattr(view, "st", dummy)

    updated_df = pd.DataFrame([{"id": "1"}])
    mocker.patch("views.api_configurazione.validate_preset", return_value=(True, ""))
    mocker.patch(
        "views.api_configurazione.save_preset",
        return_value=(True, "saved", updated_df),
    )
    view.save_preset_from_form()

    assert dummy.session_state.api_presets is updated_df
    assert dummy.successes == ["saved"]
    assert dummy.session_state.editing_preset is False
    assert dummy.session_state.current_preset_edit_id is None
    assert dummy.session_state.preset_form_data == {}


def test_delete_preset_callback_clears_form_state(monkeypatch, mocker):
    dummy = DummySt()
    dummy.session_state.update(
        {
            "api_presets": pd.DataFrame([{"id": "2"}]),
            "editing_preset": True,
            "current_preset_edit_id": "2",
            "preset_form_data": {"name": "Old"},
        }
    )
    monkeypatch.setattr(view, "st", dummy)

    updated_df = pd.DataFrame([])
    mocker.patch(
        "views.api_configurazione.delete_preset",
        return_value=(True, "deleted", updated_df),
    )
    view.delete_preset_callback("2")

    assert dummy.session_state.api_presets is updated_df
    assert dummy.successes == ["deleted"]
    assert dummy.session_state.editing_preset is False
    assert dummy.session_state.current_preset_edit_id is None
    assert dummy.session_state.preset_form_data == {}
