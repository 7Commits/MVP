import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import result_controller as controller  # noqa: E402


def sample_data():
    results_df = pd.DataFrame(
        [
            {
                "id": "1",
                "set_id": "10",
                "timestamp": "2024-01-01",
                "results": {
                    "generation_llm": "gpt-3.5",
                    "avg_score": 80,
                    "method": "LLM",
                },
            },
            {
                "id": "2",
                "set_id": "20",
                "timestamp": "2024-01-02",
                "results": {
                    "generation_preset": "presetA",
                    "avg_score": 70,
                    "method": "LLM",
                },
            },
            {
                "id": "3",
                "set_id": "10",
                "timestamp": "2024-01-03",
                "results": {
                    "generation_llm": "gpt-4",
                    "avg_score": 90,
                    "method": "LLM",
                },
            },
        ]
    )
    sets_df = pd.DataFrame(
        [
            {"id": "10", "name": "Set1"},
            {"id": "20", "name": "Set2"},
        ]
    )
    presets_df = pd.DataFrame(
        [
            {"name": "presetA", "model": "gpt-3.5"},
        ]
    )
    return results_df, sets_df, presets_df


def test_get_results_filters(mocker):
    results_df, sets_df, presets_df = sample_data()
    mocker.patch("controllers.result_controller.load_results", return_value=results_df)
    mocker.patch("controllers.result_controller.load_sets", return_value=sets_df)
    mocker.patch("controllers.result_controller.load_presets", return_value=presets_df)

    df_set = controller.get_results("Set1", None)
    assert set(df_set["id"]) == {"1", "3"}

    df_model = controller.get_results(None, "gpt-3.5")
    assert set(df_model["id"]) == {"1", "2"}


def test_list_names(mocker):
    results_df, sets_df, presets_df = sample_data()
    mocker.patch("controllers.result_controller.load_presets", return_value=presets_df)

    set_names = controller.list_set_names(results_df, sets_df)
    assert set_names == ["Set1", "Set2"]

    model_names = controller.list_model_names(results_df)
    assert model_names == ["gpt-3.5", "gpt-4"]


def test_prepare_select_options():
    results_df, sets_df, _ = sample_data()
    options = controller.prepare_select_options(results_df, sets_df)
    expected = {
        "3": "2024-01-03 - 🤖 Set1 (Avg: 90.00%) - LLM",
        "2": "2024-01-02 - 🤖 Set2 (Avg: 70.00%) - LLM",
        "1": "2024-01-01 - 🤖 Set1 (Avg: 80.00%) - LLM",
    }
    assert options == expected
