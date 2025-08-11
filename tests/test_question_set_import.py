import os
import sys
from unittest.mock import patch

import pandas as pd
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.question_set import QuestionSet


data_dir = os.path.join(os.path.dirname(__file__), "sample_data")


@pytest.mark.parametrize("filename", ["question_sets.json", "question_sets.csv"])
@patch("controllers.question_controller.add_question_if_not_exists")
@patch("models.question_set.QuestionSet.create")
@patch("controllers.question_set_controller.load_sets")
@patch("controllers.question_controller.load_questions")
@patch("utils.cache.refresh_question_sets", return_value=pd.DataFrame())
def test_import_from_file_handles_duplicates(
    mock_refresh,
    mock_load_questions,
    mock_load_sets,
    mock_create,
    mock_add_question,
    filename,
):
    mock_load_questions.return_value = pd.DataFrame(
        {"id": ["q1"], "domanda": ["Existing"], "risposta_attesa": ["A1"], "categoria": ["cat1"]}
    )
    mock_load_sets.return_value = pd.DataFrame(
        {"id": ["s1"], "name": ["Set1"], "questions": [[]]}
    )
    mock_add_question.side_effect = lambda question_id, domanda, risposta_attesa, categoria: question_id == "q2"

    with open(os.path.join(data_dir, filename), "r", encoding="utf-8") as f:
        result = QuestionSet.import_from_file(f)

    assert result.sets_imported_count == 1
    assert result.new_questions_added_count == 1
    assert result.existing_questions_found_count == 1
    assert any("Set1" in w for w in result.warnings)
    assert any("senza ID" in w for w in result.warnings)
    mock_create.assert_called_once_with("Set2", ["q1", "q2"])
    assert mock_add_question.call_count == 1

