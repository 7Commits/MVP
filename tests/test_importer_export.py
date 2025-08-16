import pandas as pd
from models.question import Question, question_importer
from models.question_set import QuestionSet, question_set_importer
from models.test_result import TestResult, test_result_importer


def test_question_gather_data(mocker):
    mocker.patch(
        "models.question.Question.load_all",
        return_value=[Question(id="1", domanda="d", risposta_attesa="a", categoria="c")],
    )
    df = question_importer.gather_data()
    assert df.to_dict(orient="records") == [
        {"id": "1", "domanda": "d", "risposta_attesa": "a", "categoria": "c"}
    ]


def test_question_set_gather_data(mocker):
    mocker.patch(
        "models.question.Question.load_all",
        return_value=[Question(id="1", domanda="d", risposta_attesa="a", categoria="c")],
    )
    mocker.patch(
        "models.question_set.QuestionSet.load_all",
        return_value=[QuestionSet(id="s1", name="S1", questions=["1"])]
    )
    data = question_set_importer.gather_data()
    assert data == [
        {"name": "S1", "questions": [
            {"id": "1", "domanda": "d", "risposta_attesa": "a", "categoria": "c"}
        ]}
    ]


def test_test_result_gather_data(mocker):
    df = pd.DataFrame([
        {"id": "1", "set_id": "s", "timestamp": "t", "results": {}}
    ])
    mocker.patch(
        "models.test_result.TestResult.load_all_df",
        return_value=df,
    )
    result = test_result_importer.gather_data()
    assert result.equals(df)
