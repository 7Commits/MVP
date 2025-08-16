import os
import sys

import pandas as pd
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.test_result import TestResult, test_result_importer


data_dir = os.path.join(os.path.dirname(__file__), "sample_data")


@pytest.mark.parametrize("filename", ["test_results.csv", "test_results.json"])
def test_import_from_file_skips_duplicates_and_saves(mocker, filename):
    mock_load = mocker.patch("models.test_result.TestResult.load_all_df")
    mock_save = mocker.patch("models.test_result.TestResult.save")
    mock_refresh = mocker.patch("models.test_result.TestResult.refresh_cache")
    mock_load.return_value = pd.DataFrame(
        [{"id": "1", "set_id": "s1", "timestamp": "t0", "results": {}}]
    )
    with open(os.path.join(data_dir, filename), "r", encoding="utf-8") as f:
        result = test_result_importer.import_from_file(f)

    assert result["success"] is True
    assert result["message"] == "Importati 1 risultati."
    mock_save.assert_called_once()
    saved = mock_save.call_args[0][0]
    assert {r.id for r in saved} == {"1", "2"}
    mock_refresh.assert_called_once()

