import json
import logging
import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers.test_controller import evaluate_answer  # noqa: E402


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


@patch("utils.openai_client.get_openai_client")
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

    result = evaluate_answer(
        "q", "expected", "actual", {"api_key": "key"}
    )

    assert result["score"] == 90
    assert result["similarity"] == 90


@patch("utils.openai_client.get_openai_client", return_value=None)
def test_evaluate_answer_no_client(mock_get_client):
    with pytest.raises(ValueError):
        evaluate_answer(
            "q", "expected", "actual", {"api_key": None}
        )


@patch("utils.openai_client.get_openai_client")
def test_evaluate_answer_json_decode_error(mock_get_client):
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response("not json")

    with pytest.raises(ValueError):
        evaluate_answer(
            "q", "expected", "actual", {"api_key": "key"}
        )


@patch("utils.openai_client.get_openai_client")
def test_evaluate_answer_no_choices(mock_get_client, caplog):
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response_no_choices()

    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError):
            evaluate_answer(
                "q", "expected", "actual", {"api_key": "key"}
            )

    assert "choices" in caplog.text
