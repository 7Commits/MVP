import os
import sys
from unittest.mock import Mock, patch

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import openai_controller  # noqa: E402


def _mock_response(content: str):
    mock_resp = Mock()
    mock_choice = Mock()
    mock_choice.message = Mock()
    mock_choice.message.content = content
    mock_resp.choices = [mock_choice]
    return mock_resp


@patch("controllers.openai_controller.evaluation_service.evaluate_answer")
def test_evaluate_answer_delegates(mock_service):
    evaluation = {
        "score": 90,
        "explanation": "good",
        "similarity": 90,
        "correctness": 90,
        "completeness": 90,
    }
    mock_service.return_value = evaluation

    result = openai_controller.evaluate_answer(
        "q", "expected", "actual", {"api_key": "key"}, show_api_details=True
    )

    assert result == evaluation
    mock_service.assert_called_once_with(
        "q", "expected", "actual", {"api_key": "key"}, True
    )


@patch("services.openai_service.get_openai_client")
def test_generate_example_answer_success(mock_get_client):
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response(" answer ")

    result = openai_controller.generate_example_answer_with_llm(
        "question", {"api_key": "key"}
    )

    assert result["answer"] == "answer"


@patch("services.openai_service.get_openai_client", return_value=None)
def test_generate_example_answer_no_client(mock_get_client):
    result = openai_controller.generate_example_answer_with_llm(
        "question", {"api_key": None}, show_api_details=True
    )

    assert result["answer"] is None
    assert result["api_details"]["error"] == "Client API non configurato"


@patch("services.openai_service.get_openai_client")
def test_generate_example_answer_empty_question(mock_get_client):
    mock_get_client.return_value = Mock()

    result = openai_controller.generate_example_answer_with_llm(
        "", {"api_key": "key"}, show_api_details=True
    )

    assert result["answer"] is None
    assert result["api_details"]["error"] == "Domanda vuota o non valida"


@patch("services.openai_service.get_openai_client")
def test_test_api_connection_success(mock_get_client):
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response(
        "Connessione riuscita."
    )

    ok, msg = openai_controller.test_api_connection(
        "key", "endpoint", "model", 0.1, 10
    )

    assert ok is True
    assert msg == "Connessione API riuscita!"


@patch("services.openai_service.get_openai_client")
def test_test_api_connection_unexpected_response(mock_get_client):
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response("failure")

    ok, msg = openai_controller.test_api_connection(
        "key", "endpoint", "model", 0.1, 10
    )

    assert ok is False
    assert "Risposta inattesa" in msg


@patch("services.openai_service.get_openai_client", return_value=None)
def test_test_api_connection_no_client(mock_get_client):
    ok, msg = openai_controller.test_api_connection(
        "key", "endpoint", "model", 0.1, 10
    )

    assert ok is False
    assert "Client API non inizializzato" in msg
