import os
import sys

import pytest

# Aggiunge la cartella principale al percorso dei moduli per i test
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import api_preset_controller  # noqa: E402
from controllers.test_controller import generate_answer  # noqa: E402


def _mock_response(mocker, content: str):
    """Crea una risposta simulata con il contenuto fornito."""
    mock_resp = mocker.Mock()
    mock_choice = mocker.Mock()
    mock_choice.message = mocker.Mock()
    mock_choice.message.content = content
    mock_resp.choices = [mock_choice]
    return mock_resp


def test_generate_answer_success(mocker):
    mock_get_client = mocker.patch("utils.openai_client.get_openai_client")
    mock_client = mocker.Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response(
        mocker, " answer "
    )

    result = generate_answer("question", {"api_key": "key"})

    assert result == "answer"


def test_generate_answer_no_client(mocker):
    mocker.patch("utils.openai_client.get_openai_client", return_value=None)
    with pytest.raises(ValueError):
        generate_answer("question", {"api_key": None})


def test_generate_answer_empty_question(mocker):
    mock_get_client = mocker.patch("utils.openai_client.get_openai_client")
    mock_get_client.return_value = mocker.Mock()

    with pytest.raises(ValueError):
        generate_answer("", {"api_key": "key"})


def test_test_api_connection_success(mocker):
    mock_get_client = mocker.patch("utils.openai_client.get_openai_client")
    mock_client = mocker.Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response(
        mocker, "Connessione riuscita."
    )

    ok, msg = api_preset_controller.test_api_connection(
        "key", "endpoint", "model", 0.1, 10
    )

    assert ok is True
    assert msg == "Connessione API riuscita!"


def test_test_api_connection_unexpected_response(mocker):
    mock_get_client = mocker.patch("utils.openai_client.get_openai_client")
    mock_client = mocker.Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response(
        mocker, "failure"
    )

    ok, msg = api_preset_controller.test_api_connection(
        "key", "endpoint", "model", 0.1, 10
    )

    assert ok is False
    assert "Risposta inattesa" in msg


def test_test_api_connection_no_client(mocker):
    mocker.patch("utils.openai_client.get_openai_client", return_value=None)
    ok, msg = api_preset_controller.test_api_connection(
        "key", "endpoint", "model", 0.1, 10
    )

    assert ok is False
    assert "Client API non inizializzato" in msg
