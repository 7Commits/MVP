import os
import sys
from unittest.mock import patch


sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import question_controller  # noqa: E402


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.Question.update")
def test_update_question_success(mock_update, mock_refresh):
    mock_update.return_value = True

    result = question_controller.update_question(
        "qid", domanda="d", risposta_attesa="a", categoria="c"
    )

    assert result is True
    mock_update.assert_called_once_with("qid", "d", "a", "c")
    mock_refresh.assert_called_once()


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.Question.update")
def test_update_question_failure(mock_update, mock_refresh):
    mock_update.return_value = False

    result = question_controller.update_question("qid")

    assert result is False
    mock_update.assert_called_once_with("qid", None, None, None)
    mock_refresh.assert_called_once()
