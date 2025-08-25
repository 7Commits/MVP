import json
import os
import pandas as pd
from utils.file_writer_utils import write_dataset


def test_write_dataset_csv(tmp_path):
    df = pd.DataFrame([{"a": 1, "b": 2}])
    path = tmp_path / "out.csv"
    write_dataset(df, path)
    assert path.exists()
    loaded = pd.read_csv(path)
    assert loaded.iloc[0]["a"] == 1


def test_write_dataset_json(tmp_path):
    data = [{"a": 1}, {"a": 2}]
    path = tmp_path / "out.json"
    write_dataset(data, path)
    with open(path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded[1]["a"] == 2
