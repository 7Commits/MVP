import io
import json

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pandas as pd  # noqa: E402
import pytest  # noqa: E402

from models.question_set import (
    QuestionSet,
    PersistSetsResult,
)
from utils.file_reader_utils import read_question_sets


def test_read_question_sets_csv_missing_columns():
    csv_content = "name,id,domanda\nset1,1,Domanda"
    file = io.StringIO(csv_content)
    file.name = "test.csv"
    with pytest.raises(ValueError):
        read_question_sets(file)


def test_read_question_sets_json_not_list():
    data = {"name": "set1"}
    file = io.BytesIO(json.dumps(data).encode("utf-8"))
    file.name = "test.json"
    with pytest.raises(ValueError):
        read_question_sets(file)


def test_resolve_question_ids_adds_and_existing(mocker):
    mock_add = mocker.patch(
        "controllers.question_controller.add_question_if_not_exists"
    )
    mock_add.return_value = True
    current_questions = pd.DataFrame(
        [{"id": "2", "domanda": "", "risposta_attesa": "", "categoria": ""}]
    )
    questions = [
        {"id": "1", "domanda": "Q1", "risposta_attesa": "A1", "categoria": ""},
        {"id": "2"},
    ]
    (
        ids,
        updated_df,
        new_added,
        existing_found,
        warnings,
    ) = QuestionSet._resolve_question_ids(questions, current_questions)
    assert ids == ["1", "2"]
    assert new_added == 1
    assert existing_found == 1
    assert warnings == []
    assert "1" in updated_df["id"].values
    mock_add.assert_called_once()


def test_resolve_question_ids_missing_id():
    current_questions = pd.DataFrame(
        columns=["id", "domanda", "risposta_attesa", "categoria"]
    )
    questions = [{"domanda": "Q", "risposta_attesa": "A"}]
    (
        ids,
        updated_df,
        new_added,
        existing_found,
        warnings,
    ) = QuestionSet._resolve_question_ids(questions, current_questions)
    assert ids == []
    assert new_added == 0
    assert existing_found == 0
    assert len(warnings) == 1
    assert updated_df.empty


def test_persist_sets_skips_duplicates(mocker):
    mock_refresh = mocker.patch("utils.cache.refresh_question_sets")
    mock_create = mocker.patch("models.question_set.QuestionSet.create")
    mock_refresh.return_value = pd.DataFrame(
        [{"id": "s1", "name": "Existing", "questions": []}]
    )
    current_questions = pd.DataFrame(
        columns=["id", "domanda", "risposta_attesa", "categoria"]
    )
    current_sets = pd.DataFrame(
        [{"id": "s1", "name": "Existing", "questions": []}]
    )
    sets_data = [
        {"name": "Existing", "questions": []},
        {"name": "New", "questions": []},
    ]
    result = QuestionSet._persist_entities(sets_data, current_questions, current_sets)
    assert result.sets_imported_count == 1
    assert result.new_questions_added_count == 0
    assert result.existing_questions_found_count == 0
    assert any("esiste già" in w for w in result.warnings)
    mock_create.assert_called_once_with("New", [])
