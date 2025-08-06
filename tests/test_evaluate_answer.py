import json
import logging
import os
import sys
from unittest.mock import Mock, patch

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import test_controller  # noqa: E402


def _mock_response(content: str):
    mock_resp = Mock()
    mock_choice = Mock()
    mock_choice.message = Mock()
    mock_choice.message.content = content
    mock_resp.choices = [mock_choice]
    return mock_resp


def _mock_response_no_choices():
    mock_resp = Mock()
    mock_resp.choices = []
    return mock_resp


@patch("controllers.test_controller.openai_client.get_openai_client")
def test_evaluate_answer_success(mock_get_client):
    mock_client = Mock()
    mock_get_client.return_value = mock_client

    evaluation = {
        "score": 90,
        "explanation": "good",
        "similarity": 90,
        "correctness": 90,
        "completeness": 90,
    }
    mock_client.chat.completions.create.return_value = _mock_response(
        json.dumps(evaluation)
    )

    result = test_controller.evaluate_answer(
        "q", "expected", "actual", {"api_key": "key"}, show_api_details=True
    )

    assert result["score"] == 90
    assert result["similarity"] == 90
    assert "api_details" in result


@patch("controllers.test_controller.openai_client.get_openai_client", return_value=None)
def test_evaluate_answer_no_client(mock_get_client):
    result = test_controller.evaluate_answer(
        "q", "expected", "actual", {"api_key": None}
    )

    assert result["score"] == 0
    assert "Client API" in result["explanation"]


@patch("controllers.test_controller.openai_client.get_openai_client")
def test_evaluate_answer_json_decode_error(mock_get_client):
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response("not json")

    result = test_controller.evaluate_answer(
        "q", "expected", "actual", {"api_key": "key"}
    )

    assert result["score"] == 0
    assert "Errore di decodifica JSON" in result["explanation"]


@patch("controllers.test_controller.openai_client.get_openai_client")
def test_evaluate_answer_no_choices(mock_get_client, caplog):
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response_no_choices()

    with caplog.at_level(logging.ERROR):
        result = test_controller.evaluate_answer(
            "q", "expected", "actual", {"api_key": "key"}
        )

    assert result["score"] == 0
    assert "choices" in caplog.text
