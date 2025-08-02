import pandas as pd
from unittest.mock import patch

from services import question_service


@patch("services.question_service.refresh_questions")
@patch("services.question_service.Question.add")
@patch("services.question_service.Question.load_all")
def test_add_question_if_not_exists_existing(mock_load_all, mock_add, mock_refresh):
    mock_load_all.return_value = pd.DataFrame({"id": ["123"]})

    result = question_service.add_question_if_not_exists(
        question_id="123",
        domanda="dom",
        risposta_attesa="ans",
        categoria="cat",
    )

    assert result is False
    mock_add.assert_not_called()
    mock_refresh.assert_not_called()


@patch("services.question_service.refresh_questions")
@patch("services.question_service.Question.add")
@patch("services.question_service.Question.load_all")
def test_add_question_if_not_exists_new(mock_load_all, mock_add, mock_refresh):
    mock_load_all.return_value = pd.DataFrame({"id": ["456"]})

    result = question_service.add_question_if_not_exists(
        question_id="123",
        domanda="dom",
        risposta_attesa="ans",
        categoria="cat",
    )

    assert result is True
    mock_add.assert_called_once_with("dom", "ans", "cat", "123")
    mock_refresh.assert_called_once()
