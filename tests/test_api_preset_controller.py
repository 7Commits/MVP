import os
import sys
from unittest.mock import Mock, patch

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import api_preset_controller as controller  # noqa: E402


@patch("controllers.api_preset_controller.load_presets")
def test_validate_preset_empty_name(mock_load):
    ok, msg = controller.validate_preset({"name": ""})
    assert ok is False
    assert "non può essere vuoto" in msg
    mock_load.assert_not_called()


@patch("controllers.api_preset_controller.load_presets")
def test_validate_preset_duplicate(mock_load):
    mock_load.return_value = pd.DataFrame({"id": ["1"], "name": ["A"]})
    ok, msg = controller.validate_preset({"name": "A"})
    assert ok is False
    assert "esiste già" in msg


@patch("controllers.api_preset_controller.load_presets")
def test_validate_preset_ok(mock_load):
    mock_load.return_value = pd.DataFrame({"id": ["1"], "name": ["A"]})
    ok, msg = controller.validate_preset({"name": "B"})
    assert ok is True
    assert msg == ""


@patch("controllers.api_preset_controller.refresh_api_presets")
@patch("controllers.api_preset_controller.APIPreset.save_df")
@patch("controllers.api_preset_controller.load_presets")
@patch("controllers.api_preset_controller.uuid.uuid4", return_value="new-id")
def test_save_preset_new(mock_uuid, mock_load, mock_save_df, mock_refresh):
    df = pd.DataFrame([
        {
            "id": "1",
            "name": "Old",
            "endpoint": "e",
            "api_key": "k",
            "model": "m",
            "temperature": 0.0,
            "max_tokens": 100,
        }
    ])
    mock_load.return_value = df
    updated_df = pd.DataFrame([])
    mock_refresh.return_value = updated_df

    ok, msg, returned_df = controller.save_preset(
        {
            "name": "New",
            "endpoint": "e",
            "api_key": "k",
            "model": "m",
            "temperature": 0.1,
            "max_tokens": 50,
        }
    )

    assert ok is True
    assert "creato" in msg
    assert returned_df is updated_df
    mock_save_df.assert_called_once()
    saved_df = mock_save_df.call_args[0][0]
    assert "new-id" in saved_df["id"].values
    assert "New" in saved_df["name"].values


@patch("controllers.api_preset_controller.refresh_api_presets")
@patch("controllers.api_preset_controller.APIPreset.delete")
@patch("controllers.api_preset_controller.load_presets")
def test_delete_preset(mock_load, mock_delete, mock_refresh):
    df = pd.DataFrame([
        {
            "id": "1",
            "name": "Old",
            "endpoint": "e",
            "api_key": "k",
            "model": "m",
            "temperature": 0.0,
            "max_tokens": 100,
        }
    ])
    mock_load.return_value = df
    updated_df = pd.DataFrame([])
    mock_refresh.return_value = updated_df

    ok, msg, returned_df = controller.delete_preset("1")
    assert ok is True
    assert "eliminato" in msg
    assert returned_df is updated_df
    mock_delete.assert_called_once_with("1")


@patch("controllers.api_preset_controller.openai_client.get_openai_client")
def test_test_api_connection_delegates(mock_get_client):
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_choice = Mock()
    mock_choice.message = Mock()
    mock_choice.message.content = "Connessione riuscita."
    mock_resp = Mock()
    mock_resp.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_resp

    ok, msg = controller.test_api_connection("k", "e", "m", 0.1, 10)

    assert ok is True
    assert "riuscita" in msg.lower()
    mock_get_client.assert_called_once_with(api_key="k", base_url="e")
