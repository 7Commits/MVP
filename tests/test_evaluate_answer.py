import json
import logging
import os
import sys

import pytest

from utils.openai_client import ClientCreationError

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers.test_controller import evaluate_answer  # noqa: E402


def _mock_response(mocker, content: str):
    mock_resp = mocker.Mock()
    mock_choice = mocker.Mock()
    mock_choice.message = mocker.Mock()
    mock_choice.message.content = content
    mock_resp.choices = [mock_choice]
    return mock_resp


def _mock_response_no_choices(mocker):
    mock_resp = mocker.Mock()
    mock_resp.choices = []
    return mock_resp


def test_evaluate_answer_success(mocker):
    mock_get_client = mocker.patch("utils.openai_client.get_openai_client")
    mock_client = mocker.Mock()
    mock_get_client.return_value = mock_client

    evaluation = {
        "score": 90,
        "explanation": "good",
        "similarity": 90,
        "correctness": 90,
        "completeness": 90,
    }
    mock_client.chat.completions.create.return_value = _mock_response(
        mocker, json.dumps(evaluation)
    )

    result = evaluate_answer(
        "q", "expected", "actual", {"api_key": "key"}
    )

    assert result["score"] == 90
    assert result["similarity"] == 90


def test_evaluate_answer_no_client(mocker):
    mocker.patch(
        "utils.openai_client.get_openai_client",
        side_effect=ClientCreationError("boom"),
    )
    with pytest.raises(ValueError):
        evaluate_answer(
            "q", "expected", "actual", {"api_key": None}
        )


def test_evaluate_answer_json_decode_error(mocker):
    mock_get_client = mocker.patch("utils.openai_client.get_openai_client")
    mock_client = mocker.Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response(
        mocker, "not json"
    )

    with pytest.raises(ValueError):
        evaluate_answer(
            "q", "expected", "actual", {"api_key": "key"}
        )


def test_evaluate_answer_no_choices(mocker, caplog):
    mock_get_client = mocker.patch("utils.openai_client.get_openai_client")
    mock_client = mocker.Mock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_response_no_choices(mocker)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError):
            evaluate_answer(
                "q", "expected", "actual", {"api_key": "key"}
            )

    assert "choices" in caplog.text
