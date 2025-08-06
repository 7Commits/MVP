import os
import sys
from unittest.mock import patch

import io
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import question_controller  # noqa: E402


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.Question.add")
@patch("controllers.question_controller.load_questions")
def test_add_question_if_not_exists_existing(
    mock_load_questions, mock_add, mock_refresh
):
    mock_load_questions.return_value = pd.DataFrame({"id": ["123"]})

    result = question_controller.add_question_if_not_exists(
        question_id="123",
        domanda="dom",
        risposta_attesa="ans",
        categoria="cat",
    )

    assert result is False
    mock_add.assert_not_called()
    mock_refresh.assert_not_called()


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.Question.add")
@patch("controllers.question_controller.load_questions")
def test_add_question_if_not_exists_new(mock_load_questions, mock_add, mock_refresh):
    mock_load_questions.return_value = pd.DataFrame({"id": ["456"]})

    result = question_controller.add_question_if_not_exists(
        question_id="123",
        domanda="dom",
        risposta_attesa="ans",
        categoria="cat",
    )

    assert result is True
    mock_add.assert_called_once_with("dom", "ans", "cat", "123")
    mock_refresh.assert_called_once()


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.Question.add")
def test_add_question(mock_add, mock_refresh):
    mock_add.return_value = "qid"

    result = question_controller.add_question("dom", "ans", "cat", "qid")

    assert result == "qid"
    mock_add.assert_called_once_with("dom", "ans", "cat", "qid")
    mock_refresh.assert_called_once()


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.Question.update")
def test_update_question(mock_update, mock_refresh):
    mock_update.return_value = True

    result = question_controller.update_question("qid", "dom", "ans", "cat")

    assert result is True
    mock_update.assert_called_once_with("qid", "dom", "ans", "cat")
    mock_refresh.assert_called_once()


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.Question.delete")
def test_delete_question(mock_delete, mock_refresh):
    question_controller.delete_question("qid")

    mock_delete.assert_called_once_with("qid")
    mock_refresh.assert_called_once()


def test_import_questions_from_file_invalid_json():
    file = io.StringIO("not json")
    file.name = "bad.json"
    success, message = question_controller.import_questions_from_file(file)
    assert not success
    assert message == "Il formato del file json non è valido"


def test_import_questions_from_file_invalid_csv():
    file = io.StringIO("id,domanda\n\"1,Test")
    file.name = "bad.csv"
    success, message = question_controller.import_questions_from_file(file)
    assert not success
    assert message == "Il formato del file csv non è valido"
