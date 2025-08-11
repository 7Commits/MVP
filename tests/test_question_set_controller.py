import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import question_set_controller  # noqa: E402


def test_create_set_controller(mocker):
    mock_refresh = mocker.patch(
        "controllers.question_set_controller.refresh_question_sets"
    )
    mock_create = mocker.patch(
        "controllers.question_set_controller.QuestionSet.create"
    )
    mock_create.return_value = "sid"

    result = question_set_controller.create_set("name", ["q1"])

    assert result == "sid"
    mock_create.assert_called_once_with("name", ["q1"])
    mock_refresh.assert_called_once()


def test_update_set_controller(mocker):
    mock_refresh = mocker.patch(
        "controllers.question_set_controller.refresh_question_sets"
    )
    mock_update = mocker.patch(
        "controllers.question_set_controller.QuestionSet.update"
    )
    question_set_controller.update_set("sid", name="name", question_ids=["q1"])

    mock_update.assert_called_once_with("sid", "name", ["q1"])
    mock_refresh.assert_called_once()


def test_delete_set_controller(mocker):
    mock_refresh = mocker.patch(
        "controllers.question_set_controller.refresh_question_sets"
    )
    mock_delete = mocker.patch(
        "controllers.question_set_controller.QuestionSet.delete"
    )
    question_set_controller.delete_set("sid")

    mock_delete.assert_called_once_with("sid")
    mock_refresh.assert_called_once()


def test_prepare_sets_for_view(mocker):
    mock_get_sets = mocker.patch(
        "controllers.question_set_controller._get_question_sets"
    )
    mock_get_questions = mocker.patch(
        "controllers.question_set_controller._get_questions"
    )
    questions_df = pd.DataFrame(
        {
            "id": ["1", "2"],
            "domanda": ["d1", "d2"],
            "risposta_attesa": ["a1", "a2"],
            "categoria": ["A", "B"],
        }
    )
    sets_df = pd.DataFrame(
        {
            "id": ["s1", "s2"],
            "name": ["set1", "set2"],
            "questions": [["1"], ["2"]],
        }
    )

    mock_get_questions.return_value = questions_df
    mock_get_sets.return_value = sets_df

    result = question_set_controller.prepare_sets_for_view(["A"])

    assert result["categories"] == ["A", "B"]
    assert result["sets_df"]["id"].tolist() == ["s1"]
    assert result["sets_df"].iloc[0]["questions_detail"] == [
        {"id": "1", "domanda": "d1", "categoria": "A"}
    ]
