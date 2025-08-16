import os
import sys

import pandas as pd
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import question_controller  # noqa: E402


def test_add_question_if_not_exists_existing(mocker):
    mock_refresh = mocker.patch("controllers.question_controller.refresh_questions")
    mock_add = mocker.patch("controllers.question_controller.Question.add")
    mock_load_questions = mocker.patch(
        "controllers.question_controller.load_questions"
    )
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


def test_add_question_if_not_exists_new(mocker):
    mock_refresh = mocker.patch("controllers.question_controller.refresh_questions")
    mock_add = mocker.patch("controllers.question_controller.Question.add")
    mock_load_questions = mocker.patch(
        "controllers.question_controller.load_questions"
    )
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


def test_add_question(mocker):
    mock_refresh = mocker.patch("controllers.question_controller.refresh_questions")
    mock_add = mocker.patch("controllers.question_controller.Question.add")
    mock_add.return_value = "qid"

    result = question_controller.add_question("dom", "ans", "cat", "qid")

    assert result == "qid"
    mock_add.assert_called_once_with("dom", "ans", "cat", "qid")
    mock_refresh.assert_called_once()


def test_update_question(mocker):
    mock_refresh = mocker.patch("controllers.question_controller.refresh_questions")
    mock_update = mocker.patch("controllers.question_controller.Question.update")
    mock_update.return_value = True

    result = question_controller.update_question("qid", "dom", "ans", "cat")

    assert result is True
    mock_update.assert_called_once_with("qid", "dom", "ans", "cat")
    mock_refresh.assert_called_once()


def test_delete_question(mocker):
    mock_refresh = mocker.patch("controllers.question_controller.refresh_questions")
    mock_delete = mocker.patch("controllers.question_controller.Question.delete")
    question_controller.delete_question("qid")

    mock_delete.assert_called_once_with("qid")
    mock_refresh.assert_called_once()
def test_get_filtered_questions(mocker):
    mock_filter = mocker.patch(
        "controllers.question_controller.Question.filter_by_category"
    )
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


def test_filter_by_category(mocker):
    mock_get_questions = mocker.patch("utils.cache.get_questions")
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


def test_filter_by_category_no_category_column(mocker):
    mock_get_questions = mocker.patch("utils.cache.get_questions")
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


def test_filter_by_category_empty_df(mocker):
    mock_get_questions = mocker.patch("utils.cache.get_questions")
    mock_get_questions.return_value = pd.DataFrame()

    filtered_df, categories = question_controller.Question.filter_by_category()
    assert filtered_df.empty
    assert categories == []


def test_export_questions_action(mocker, tmp_path):
    mock_export = mocker.patch(
        "controllers.question_controller.question_importer.export_to_file"
    )
    dest = tmp_path / "qs.csv"
    question_controller.export_questions_action(dest)
    mock_export.assert_called_once_with(dest)


def test_get_question_text_found(mocker):
    mock_refresh = mocker.patch("controllers.question_controller.refresh_questions")
    mock_load = mocker.patch("controllers.question_controller.load_questions")
    mock_load.return_value = pd.DataFrame({"id": ["1"], "domanda": ["Q1"]})
    text = question_controller.get_question_text("1")
    mock_refresh.assert_not_called()
    assert text == "Q1"


def test_get_question_text_refresh(mocker):
    mock_refresh = mocker.patch("controllers.question_controller.refresh_questions")
    mock_load = mocker.patch("controllers.question_controller.load_questions")
    mock_load.return_value = pd.DataFrame({"id": ["1"]})
    mock_refresh.return_value = pd.DataFrame({"id": ["1"], "domanda": ["Q1"]})
    text = question_controller.get_question_text("1")
    mock_refresh.assert_called_once()
    assert text == "Q1"


def test_get_question_category_found(mocker):
    mock_refresh = mocker.patch("controllers.question_controller.refresh_questions")
    mock_load = mocker.patch("controllers.question_controller.load_questions")
    mock_load.return_value = pd.DataFrame({"id": ["1"], "categoria": ["C1"]})
    cat = question_controller.get_question_category("1")
    mock_refresh.assert_not_called()
    assert cat == "C1"


def test_get_question_category_refresh(mocker):
    mock_refresh = mocker.patch("controllers.question_controller.refresh_questions")
    mock_load = mocker.patch("controllers.question_controller.load_questions")
    mock_load.return_value = pd.DataFrame({"id": ["1"]})
    mock_refresh.return_value = pd.DataFrame({"id": ["1"], "categoria": ["C1"]})
    cat = question_controller.get_question_category("1")
    mock_refresh.assert_called_once()
    assert cat == "C1"


def test_save_question_action_success(mocker):
    mock_refresh = mocker.patch("controllers.question_controller.refresh_questions")
    mock_update = mocker.patch("controllers.question_controller.update_question")
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


def test_save_question_action_failure(mocker):
    mock_refresh = mocker.patch("controllers.question_controller.refresh_questions")
    mock_update = mocker.patch("controllers.question_controller.update_question")
    mock_update.return_value = False
    result = question_controller.save_question_action("1", "q", "a", "c")

    mock_refresh.assert_not_called()
    assert result["success"] is False
    assert result["questions_df"] is None


def test_delete_question_action(mocker):
    mock_refresh = mocker.patch("controllers.question_controller.refresh_questions")
    mock_delete = mocker.patch("controllers.question_controller.delete_question")
    df = pd.DataFrame()
    mock_refresh.return_value = df

    result = question_controller.delete_question_action("1")

    mock_delete.assert_called_once_with("1")
    mock_refresh.assert_called_once()
    assert result.equals(df)


def test_import_questions_action_success(mocker):
    mock_refresh = mocker.patch("controllers.question_controller.refresh_questions")
    mock_import = mocker.patch(
        "controllers.question_controller.question_importer.import_from_file"
    )
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


def test_import_questions_action_failure(mocker):
    mock_refresh = mocker.patch("controllers.question_controller.refresh_questions")
    mock_import = mocker.patch(
        "controllers.question_controller.question_importer.import_from_file"
    )
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
