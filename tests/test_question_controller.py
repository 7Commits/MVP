import os
import sys
from unittest.mock import patch

import pandas as pd
import pytest

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
@patch("controllers.question_controller.Question.filter_by_category")
def test_get_filtered_questions(mock_filter):
    df = pd.DataFrame(
        {
            "id": ["1"],
            "domanda": ["d1"],
            "risposta_attesa": ["a1"],
            "categoria": ["cat1"],
        }
    )
    mock_filter.return_value = (df, ["cat1", "cat2"])

    questions, categories = question_controller.get_filtered_questions("cat1")
    mock_filter.assert_called_once_with("cat1")
    assert categories == ["cat1", "cat2"]
    assert questions["id"].tolist() == ["1"]


@patch("utils.cache.get_questions")
def test_filter_by_category(mock_get_questions):
    mock_get_questions.return_value = pd.DataFrame(
        {
            "id": ["1", "2"],
            "domanda": ["d1", "d2"],
            "risposta_attesa": ["a1", "a2"],
            "categoria": ["cat1", "cat2"],
        }
    )

    filtered_df, categories = question_controller.Question.filter_by_category("cat1")
    assert categories == ["cat1", "cat2"]
    assert filtered_df["id"].tolist() == ["1"]


@patch("utils.cache.get_questions")
def test_filter_by_category_no_category_column(mock_get_questions):
    mock_get_questions.return_value = pd.DataFrame(
        {
            "id": ["1"],
            "domanda": ["d1"],
            "risposta_attesa": ["a1"],
        }
    )

    filtered_df, categories = question_controller.Question.filter_by_category()
    assert "categoria" in filtered_df.columns
    assert filtered_df.iloc[0]["categoria"] == "N/A"
    assert categories == ["N/A"]


@patch("utils.cache.get_questions")
def test_filter_by_category_empty_df(mock_get_questions):
    mock_get_questions.return_value = pd.DataFrame()

    filtered_df, categories = question_controller.Question.filter_by_category()
    assert filtered_df.empty
    assert categories == []


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.load_questions")
def test_get_question_text_found(mock_load, mock_refresh):
    mock_load.return_value = pd.DataFrame({"id": ["1"], "domanda": ["Q1"]})
    text = question_controller.get_question_text("1")
    mock_refresh.assert_not_called()
    assert text == "Q1"


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.load_questions")
def test_get_question_text_refresh(mock_load, mock_refresh):
    mock_load.return_value = pd.DataFrame({"id": ["1"]})
    mock_refresh.return_value = pd.DataFrame({"id": ["1"], "domanda": ["Q1"]})
    text = question_controller.get_question_text("1")
    mock_refresh.assert_called_once()
    assert text == "Q1"


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.load_questions")
def test_get_question_category_found(mock_load, mock_refresh):
    mock_load.return_value = pd.DataFrame({"id": ["1"], "categoria": ["C1"]})
    cat = question_controller.get_question_category("1")
    mock_refresh.assert_not_called()
    assert cat == "C1"


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.load_questions")
def test_get_question_category_refresh(mock_load, mock_refresh):
    mock_load.return_value = pd.DataFrame({"id": ["1"]})
    mock_refresh.return_value = pd.DataFrame({"id": ["1"], "categoria": ["C1"]})
    cat = question_controller.get_question_category("1")
    mock_refresh.assert_called_once()
    assert cat == "C1"


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.update_question")
def test_save_question_action_success(mock_update, mock_refresh):
    mock_update.return_value = True
    df = pd.DataFrame({"id": ["1"]})
    mock_refresh.return_value = df

    result = question_controller.save_question_action("1", "q", "a", "c")

    mock_update.assert_called_once_with(
        "1", domanda="q", risposta_attesa="a", categoria="c"
    )
    mock_refresh.assert_called_once()
    assert result["success"] is True
    assert result["questions_df"].equals(df)


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.update_question")
def test_save_question_action_failure(mock_update, mock_refresh):
    mock_update.return_value = False
    result = question_controller.save_question_action("1", "q", "a", "c")

    mock_refresh.assert_not_called()
    assert result["success"] is False
    assert result["questions_df"] is None


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.delete_question")
def test_delete_question_action(mock_delete, mock_refresh):
    df = pd.DataFrame()
    mock_refresh.return_value = df

    result = question_controller.delete_question_action("1")

    mock_delete.assert_called_once_with("1")
    mock_refresh.assert_called_once()
    assert result.equals(df)


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.Question.import_from_file")
def test_import_questions_action_success(mock_import, mock_refresh):
    mock_import.return_value = {
        "success": True,
        "imported_count": 1,
        "warnings": ["w"],
    }
    df = pd.DataFrame({"id": ["1"]})
    mock_refresh.return_value = df

    uploaded_file = object()
    result = question_controller.import_questions_action(uploaded_file)

    mock_import.assert_called_once_with(uploaded_file)
    mock_refresh.assert_called_once()
    assert result["imported_count"] == 1
    assert result["warnings"] == ["w"]
    assert result["questions_df"].equals(df)


def test_import_questions_action_no_file():
    with pytest.raises(ValueError, match="Nessun file caricato."):
        question_controller.import_questions_action(None)


@patch("controllers.question_controller.refresh_questions")
@patch("controllers.question_controller.Question.import_from_file")
def test_import_questions_action_failure(mock_import, mock_refresh):
    mock_import.return_value = {
        "success": False,
        "imported_count": 0,
        "warnings": ["err"],
    }

    with pytest.raises(ValueError, match="err"):
        question_controller.import_questions_action(object())

    assert mock_import.return_value["imported_count"] == 0
    assert mock_import.return_value["warnings"] == ["err"]
    mock_refresh.assert_not_called()
