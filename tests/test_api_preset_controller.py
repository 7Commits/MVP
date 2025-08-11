import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import api_preset_controller as controller  # noqa: E402


def test_validate_preset_empty_name(mocker):
    mock_load = mocker.patch("controllers.api_preset_controller.load_presets")
    ok, msg = controller.validate_preset({"name": ""})
    assert ok is False
    assert "non può essere vuoto" in msg
    mock_load.assert_not_called()


def test_validate_preset_duplicate(mocker):
    mock_load = mocker.patch("controllers.api_preset_controller.load_presets")
    mock_load.return_value = pd.DataFrame({"id": ["1"], "name": ["A"]})
    ok, msg = controller.validate_preset({"name": "A"})
    assert ok is False
    assert "esiste già" in msg


def test_validate_preset_ok(mocker):
    mock_load = mocker.patch("controllers.api_preset_controller.load_presets")
    mock_load.return_value = pd.DataFrame({"id": ["1"], "name": ["A"]})
    ok, msg = controller.validate_preset({"name": "B"})
    assert ok is True
    assert msg == ""


def test_save_preset_new(mocker):
    mock_uuid = mocker.patch(
        "controllers.api_preset_controller.uuid.uuid4", return_value="new-id"
    )
    mock_load = mocker.patch("controllers.api_preset_controller.load_presets")
    mock_save = mocker.patch("controllers.api_preset_controller.APIPreset.save")
    mock_refresh = mocker.patch(
        "controllers.api_preset_controller.refresh_api_presets"
    )

    df = pd.DataFrame(
        [
            {
                "id": "1",
                "name": "Old",
                "endpoint": "e",
                "api_key": "k",
                "model": "m",
                "temperature": 0.0,
                "max_tokens": 100,
            }
        ]
    )
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
    mock_save.assert_called_once()
    saved_presets = mock_save.call_args[0][0]
    assert any(p.id == "new-id" for p in saved_presets)
    assert any(p.name == "New" for p in saved_presets)


def test_delete_preset(mocker):
    mock_load = mocker.patch("controllers.api_preset_controller.load_presets")
    mock_delete = mocker.patch("controllers.api_preset_controller.APIPreset.delete")
    mock_refresh = mocker.patch(
        "controllers.api_preset_controller.refresh_api_presets"
    )

    df = pd.DataFrame(
        [
            {
                "id": "1",
                "name": "Old",
                "endpoint": "e",
                "api_key": "k",
                "model": "m",
                "temperature": 0.0,
                "max_tokens": 100,
            }
        ]
    )
    mock_load.return_value = df
    updated_df = pd.DataFrame([])
    mock_refresh.return_value = updated_df

    ok, msg, returned_df = controller.delete_preset("1")
    assert ok is True
    assert "eliminato" in msg
    assert returned_df is updated_df
    mock_delete.assert_called_once_with("1")


def test_test_api_connection_delegates(mocker):
    mock_get_client = mocker.patch("utils.openai_client.get_openai_client")
    mock_client = mocker.Mock()
    mock_get_client.return_value = mock_client
    mock_choice = mocker.Mock()
    mock_choice.message = mocker.Mock()
    mock_choice.message.content = "Connessione riuscita."
    mock_resp = mocker.Mock()
    mock_resp.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_resp

    ok, msg = controller.test_api_connection("k", "e", "m", 0.1, 10)

    assert ok is True
    assert "riuscita" in msg.lower()
    mock_get_client.assert_called_once_with(api_key="k", base_url="e")

