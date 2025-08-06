import os
import sys
from unittest.mock import Mock, patch

# Aggiunge la cartella principale al percorso dei moduli per i test
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import api_preset_controller, test_controller  # noqa: E402


def _mock_response(content: str):
    """Crea una risposta simulata con il contenuto fornito."""
    mock_resp = Mock()
    mock_choice = Mock()
    mock_choice.message = Mock()
    mock_choice.message.content = content
    mock_resp.choices = [mock_choice]
    return mock_resp


@patch("controllers.test_controller.openai_client.get_openai_client")
def test_generate_example_answer_success(mock_get_client):
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response(" answer ")

    result = test_controller.generate_example_answer_with_llm(
        "question", {"api_key": "key"}
    )

    assert result["answer"] == "answer"


@patch("controllers.test_controller.openai_client.get_openai_client", return_value=None)
def test_generate_example_answer_no_client(mock_get_client):
    result = test_controller.generate_example_answer_with_llm(
        "question", {"api_key": None}, show_api_details=True
    )

    assert result["answer"] is None
    assert result["api_details"]["error"] == "Client API non configurato"


@patch("controllers.test_controller.openai_client.get_openai_client")
def test_generate_example_answer_empty_question(mock_get_client):
    mock_get_client.return_value = Mock()

    result = test_controller.generate_example_answer_with_llm(
        "", {"api_key": "key"}, show_api_details=True
    )

    assert result["answer"] is None
    assert result["api_details"]["error"] == "Domanda vuota o non valida"


@patch("controllers.api_preset_controller.openai_client.get_openai_client")
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


@patch("controllers.api_preset_controller.openai_client.get_openai_client")
def test_test_api_connection_unexpected_response(mock_get_client):
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response("failure")

    ok, msg = api_preset_controller.test_api_connection(
        "key", "endpoint", "model", 0.1, 10
    )

    assert ok is False
    assert "Risposta inattesa" in msg


@patch("controllers.api_preset_controller.openai_client.get_openai_client", return_value=None)
def test_test_api_connection_no_client(mock_get_client):
    ok, msg = api_preset_controller.test_api_connection(
        "key", "endpoint", "model", 0.1, 10
    )

    assert ok is False
    assert "Client API non inizializzato" in msg
