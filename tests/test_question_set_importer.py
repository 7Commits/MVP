import io
import json
from unittest.mock import patch

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pandas as pd  # noqa: E402
import pytest  # noqa: E402

from controllers.question_set_controller import (  # noqa: E402
    parse_input,
    resolve_question_ids,
    persist_sets,
    import_sets_from_file,
)


def test_parse_input_csv_missing_columns():
    csv_content = "name,id,domanda\nset1,1,Domanda"
    file = io.StringIO(csv_content)
    file.name = "test.csv"
    with pytest.raises(ValueError):
        parse_input(file)


def test_parse_input_json_not_list():
    data = {"name": "set1"}
    file = io.BytesIO(json.dumps(data).encode("utf-8"))
    file.name = "test.json"
    with pytest.raises(ValueError):
        parse_input(file)


@patch("controllers.question_set_controller.add_question_if_not_exists")
def test_resolve_question_ids_adds_and_existing(mock_add):
    mock_add.return_value = True
    current_questions = pd.DataFrame(
        [{"id": "2", "domanda": "", "risposta_attesa": "", "categoria": ""}]
    )
    questions = [
        {"id": "1", "domanda": "Q1", "risposta_attesa": "A1", "categoria": ""},
        {"id": "2"},
    ]
    ids, updated_df, new_added, existing_found, warnings = resolve_question_ids(
        questions, current_questions
    )
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
    ids, updated_df, new_added, existing_found, warnings = resolve_question_ids(
        questions, current_questions
    )
    assert ids == []
    assert new_added == 0
    assert existing_found == 0
    assert len(warnings) == 1
    assert updated_df.empty


@patch("controllers.question_set_controller.refresh_question_sets")
@patch("controllers.question_set_controller.QuestionSet.create")
def test_persist_sets_skips_duplicates(mock_create, mock_refresh):
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
    result = persist_sets(sets_data, current_questions, current_sets)
    assert result["sets_imported_count"] == 1
    assert any("esiste già" in w for w in result["warnings"])
    mock_create.assert_called_once_with("New", [])


def test_import_sets_from_file_none():
    result = import_sets_from_file(None)
    assert not result["success"]
    assert "Nessun file" in result["error_message"]


def test_import_sets_from_file_invalid_json():
    file = io.BytesIO(b"not json")
    file.name = "bad.json"
    result = import_sets_from_file(file)
    assert result["error_message"] == "Il formato del file json non è valido"
    assert not result["success"]


def test_import_sets_from_file_duplicates_no_error():
    data = [{"name": "Existing", "questions": []}]
    file = io.BytesIO(json.dumps(data).encode("utf-8"))
    file.name = "test.json"
    with (
        patch("controllers.question_set_controller.load_questions") as mock_lq,
        patch("controllers.question_set_controller.load_sets") as mock_ls,
        patch("controllers.question_set_controller.persist_sets") as mock_ps,
    ):
        mock_lq.return_value = pd.DataFrame()
        mock_ls.return_value = pd.DataFrame()
        mock_ps.return_value = {
            "success": False,
            "success_message": "",
            "questions_df": pd.DataFrame(),
            "sets_df": pd.DataFrame(),
            "warnings": ["dup"],
        }
        result = import_sets_from_file(file)
    assert result["error_message"] == ""
    assert result["warnings"] == ["dup"]
    assert not result["success"]
