import os
import sys
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import question_set_controller  # noqa: E402


@patch("controllers.question_set_controller.refresh_question_sets")
@patch("controllers.question_set_controller.QuestionSet.create")
def test_create_set_controller(mock_create, mock_refresh):
    mock_create.return_value = "sid"

    result = question_set_controller.create_set("name", ["q1"])

    assert result == "sid"
    mock_create.assert_called_once_with("name", ["q1"])
    mock_refresh.assert_called_once()


@patch("controllers.question_set_controller.refresh_question_sets")
@patch("controllers.question_set_controller.QuestionSet.update")
def test_update_set_controller(mock_update, mock_refresh):
    question_set_controller.update_set("sid", name="name", question_ids=["q1"])

    mock_update.assert_called_once_with("sid", "name", ["q1"])
    mock_refresh.assert_called_once()


@patch("controllers.question_set_controller.refresh_question_sets")
@patch("controllers.question_set_controller.QuestionSet.delete")
def test_delete_set_controller(mock_delete, mock_refresh):
    question_set_controller.delete_set("sid")

    mock_delete.assert_called_once_with("sid")
    mock_refresh.assert_called_once()
