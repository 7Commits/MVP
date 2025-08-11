import os
import sys
from types import SimpleNamespace

import pandas as pd
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers.test_controller import import_results_action, run_test


def test_import_results_action_no_file(mocker):
    mock_import = mocker.patch(
        "controllers.test_controller.TestResult.import_from_file"
    )
    mock_load_results = mocker.patch("controllers.test_controller.load_results")
    with pytest.raises(ValueError, match="Nessun file caricato"):
        import_results_action(None)
    mock_import.assert_not_called()
    mock_load_results.assert_not_called()


def test_import_results_action_failure(mocker):
    mock_import = mocker.patch(
        "controllers.test_controller.TestResult.import_from_file"
    )
    mock_load_results = mocker.patch("controllers.test_controller.load_results")
    mock_import.return_value = (False, "errore")
    with pytest.raises(ValueError, match="errore"):
        import_results_action("dummy")
    mock_load_results.assert_not_called()


def test_run_test_success(mocker):
    mock_load_all = mocker.patch("controllers.test_controller.Question.load_all")
    mock_gen = mocker.patch("controllers.test_controller.generate_answer")
    mock_eval = mocker.patch("controllers.test_controller.evaluate_answer")
    mock_add_refresh = mocker.patch(
        "controllers.test_controller.TestResult.add_and_refresh", return_value="rid"
    )
    mock_load_df = mocker.patch(
        "controllers.test_controller.TestResult.load_all_df",
        return_value=pd.DataFrame(),
    )
    mock_load_all.return_value = [SimpleNamespace(id="1", domanda="Q", risposta_attesa="A")]
    mock_gen.return_value = "Ans"
    mock_eval.return_value = {
        "score": 50,
        "explanation": "ok",
        "similarity": 50,
        "correctness": 50,
        "completeness": 50,
    }

    res = run_test("set1", "name", ["1"], {}, {})

    assert res["result_id"] == "rid"
    assert res["avg_score"] == 50
    assert isinstance(res["results_df"], pd.DataFrame)
    assert res["results"]["1"]["actual_answer"] == "Ans"


def test_run_test_generation_and_evaluation_errors(mocker):
    mock_load_all = mocker.patch("controllers.test_controller.Question.load_all")
    mock_gen = mocker.patch("controllers.test_controller.generate_answer")
    mock_eval = mocker.patch("controllers.test_controller.evaluate_answer")
    mock_add_refresh = mocker.patch(
        "controllers.test_controller.TestResult.add_and_refresh", return_value="rid"
    )
    mock_load_df = mocker.patch(
        "controllers.test_controller.TestResult.load_all_df",
        return_value=pd.DataFrame(),
    )
    questions = [
        SimpleNamespace(id="1", domanda="Q1", risposta_attesa="A1"),
        SimpleNamespace(id="2", domanda="Q2", risposta_attesa="A2"),
    ]
    mock_load_all.return_value = questions
    mock_gen.side_effect = [Exception("gen fail"), "ans2"]
    mock_eval.side_effect = [Exception("eval fail")]

    res = run_test("set1", "name", ["1", "2"], {}, {})

    assert res["result_id"] == "rid"
    assert res["avg_score"] == 0
    q1 = res["results"]["1"]
    q2 = res["results"]["2"]
    assert q1["actual_answer"] == "gen fail"
    assert q1["evaluation"]["score"] == 0
    assert q2["actual_answer"] == "ans2"
    assert q2["evaluation"]["score"] == 0
    assert isinstance(res["results_df"], pd.DataFrame)
