import json
import pandas as pd
import pytest

from utils.file_reader_utils import (
    read_questions,
    read_question_sets,
    read_test_results,
    filter_new_rows,
)


def test_read_questions_csv(tmp_path):
    file = tmp_path / "questions.csv"
    file.write_text("domanda,risposta_attesa\nq1,a1\n")
    with file.open("r") as f:
        df = read_questions(f)
    assert list(df.columns) == ["id", "domanda", "risposta_attesa", "categoria"]
    assert df.iloc[0]["domanda"] == "q1"


def test_read_questions_json(tmp_path):
    content = [{"domanda": "q1", "risposta_attesa": "a1"}]
    file = tmp_path / "questions.json"
    file.write_text(json.dumps(content))
    with file.open("r") as f:
        df = read_questions(f)
    assert df.iloc[0]["risposta_attesa"] == "a1"


def test_read_questions_missing_column(tmp_path):
    file = tmp_path / "bad_questions.csv"
    file.write_text("domanda\nq1\n")
    with file.open("r") as f:
        with pytest.raises(ValueError):
            read_questions(f)


def test_read_question_sets_csv(tmp_path):
    file = tmp_path / "sets.csv"
    file.write_text(
        "name,id,domanda,risposta_attesa,categoria\ns1,1,q1,a1,c1\n"
    )
    with file.open("r") as f:
        sets = read_question_sets(f)
    assert sets == [
        {
            "name": "s1",
            "questions": [
                {
                    "id": "1",
                    "domanda": "q1",
                    "risposta_attesa": "a1",
                    "categoria": "c1",
                }
            ],
        }
    ]


def test_read_question_sets_missing_columns(tmp_path):
    file = tmp_path / "bad_sets.csv"
    file.write_text("name,id,domanda\ns1,1,q1\n")
    with file.open("r") as f:
        with pytest.raises(ValueError):
            read_question_sets(f)


def test_read_test_results_csv(tmp_path):
    file = tmp_path / "results.csv"
    file.write_text("id,set_id,timestamp,results\n1,s1,2024-01-01,{}\n")
    with file.open("r") as f:
        df = read_test_results(f)
    assert df.iloc[0]["set_id"] == "s1"
    assert df.iloc[0]["results"] == {}


def test_read_test_results_invalid_json(tmp_path):
    file = tmp_path / "bad_results.json"
    file.write_text("{invalid json")
    with file.open("r") as f:
        with pytest.raises(ValueError):
            read_test_results(f)


def test_filter_new_rows_duplicates():
    df = pd.DataFrame({"id": ["a", "b", "b", "c"]})
    filtered, count = filter_new_rows(df, ["b", "d"])
    assert list(filtered["id"]) == ["a", "c"]
    assert count == 2
