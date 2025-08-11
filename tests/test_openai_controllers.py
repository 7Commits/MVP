import os
import sys
from unittest.mock import Mock, patch

import pytest

# Aggiunge la cartella principale al percorso dei moduli per i test
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import api_preset_controller  # noqa: E402
from controllers.test_controller import generate_answer  # noqa: E402


def _mock_response(content: str):
    """Crea una risposta simulata con il contenuto fornito."""
    mock_resp = Mock()
    mock_choice = Mock()
    mock_choice.message = Mock()
    mock_choice.message.content = content
    mock_resp.choices = [mock_choice]
    return mock_resp


@patch("utils.openai_client.get_openai_client")
def test_generate_answer_success(mock_get_client):
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response(" answer ")

    result = generate_answer("question", {"api_key": "key"})

    assert result == "answer"


@patch("utils.openai_client.get_openai_client", return_value=None)
def test_generate_answer_no_client(mock_get_client):
    with pytest.raises(ValueError):
        generate_answer("question", {"api_key": None})


@patch("utils.openai_client.get_openai_client")
def test_generate_answer_empty_question(mock_get_client):
    mock_get_client.return_value = Mock()

    with pytest.raises(ValueError):
        generate_answer("", {"api_key": "key"})


@patch("utils.openai_client.get_openai_client")
def test_test_api_connection_success(mock_get_client):
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response(
        "Connessione riuscita."
    )

    ok, msg = api_preset_controller.test_api_connection(
        "key", "endpoint", "model", 0.1, 10
    )

    assert ok is True
    assert msg == "Connessione API riuscita!"


@patch("utils.openai_client.get_openai_client")
def test_test_api_connection_unexpected_response(mock_get_client):
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response("failure")

    ok, msg = api_preset_controller.test_api_connection(
        "key", "endpoint", "model", 0.1, 10
    )

    assert ok is False
    assert "Risposta inattesa" in msg


@patch("utils.openai_client.get_openai_client", return_value=None)
def test_test_api_connection_no_client(mock_get_client):
    ok, msg = api_preset_controller.test_api_connection(
        "key", "endpoint", "model", 0.1, 10
    )

    assert ok is False
    assert "Client API non inizializzato" in msg
