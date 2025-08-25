"""Utility per la serializzazione di dataset in CSV o JSON."""

from __future__ import annotations

import json
import os
from typing import Any, IO, Union

import pandas as pd

__all__ = ["write_dataset"]


def _ensure_dataframe(data: Any) -> pd.DataFrame:
    """Converte ``data`` in ``DataFrame`` se possibile."""
    if isinstance(data, pd.DataFrame):
        return data
    return pd.DataFrame(data)


def write_dataset(data: Any, destination: Union[str, IO[str]]) -> None:
    """Scrive ``data`` su ``destination`` in formato CSV o JSON.

    Il formato viene determinato dall'estensione del file.
    ``destination`` può essere un percorso o un file aperto in scrittura.
    """
    close_after = False
    if isinstance(destination, (str, os.PathLike)):
        file_path = os.fspath(destination)
        ext = os.path.splitext(file_path)[1].lower()
        f: IO[str] = open(file_path, "w", encoding="utf-8", newline="")
        close_after = True
    else:
        f = destination
        name = getattr(f, "name", "")
        ext = os.path.splitext(name)[1].lower()

    if ext == ".csv":
        df = _ensure_dataframe(data)
        df.to_csv(f, index=False)
    elif ext == ".json":
        if isinstance(data, pd.DataFrame):
            payload = data.to_dict(orient="records")
        else:
            payload = data
        json.dump(payload, f, ensure_ascii=False, indent=2)
    else:
        raise ValueError("Formato file non supportato. Usare estensione .csv o .json")

    if close_after:
        f.close()
