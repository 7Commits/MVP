import os
import json
import uuid
from datetime import datetime
from typing import IO, Any, Dict, Iterable, List, Tuple

import pandas as pd

__all__ = [
    "read_questions",
    "read_question_sets",
    "read_test_results",
    "filter_new_rows",
]

REQUIRED_QUESTION_COLUMNS = ["domanda", "risposta_attesa"]
REQUIRED_SET_COLUMNS = ["name", "id", "domanda", "risposta_attesa", "categoria"]
REQUIRED_RESULT_COLUMNS = ["id", "set_id", "timestamp", "results"]


def filter_new_rows(df: pd.DataFrame, existing_ids: Iterable[str]) -> Tuple[pd.DataFrame, int]:
    """Ritorna le righe di ``df`` il cui ``id`` non è in ``existing_ids``.

    Parametri
    ---------
    df:
        DataFrame contenente una colonna ``id``.
    existing_ids:
        Insieme di identificatori già presenti nel database.

    Restituisce
    -----------
    Tuple[pd.DataFrame, int]
        Il DataFrame filtrato con sole righe nuove e il conteggio delle nuove righe.
    """

    if df is None or df.empty:
        return df, 0

    existing_set = {str(eid) for eid in existing_ids}
    mask = ~df["id"].astype(str).isin(existing_set)
    filtered = df[mask].copy()
    return filtered, int(mask.sum())


def read_questions(file: IO[str] | IO[bytes]) -> pd.DataFrame:
    """Legge un file di domande (CSV o JSON) e restituisce un DataFrame normalizzato."""
    if hasattr(file, "seek"):
        file.seek(0)
    file_extension = os.path.splitext(file.name)[1].lower()

    if file_extension == ".csv":
        try:
            df = pd.read_csv(file)
        except Exception as e:  # pragma: no cover - handled via ValueError
            raise ValueError("Il formato del file csv non è valido") from e
    elif file_extension == ".json":
        try:
            data = json.load(file)
        except Exception as e:  # pragma: no cover - handled via ValueError
            raise ValueError("Il formato del file json non è valido") from e
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and isinstance(data.get("questions"), list):
            df = pd.DataFrame(data["questions"])
        else:
            raise ValueError(
                "Il file JSON deve essere una lista di domande o contenere la chiave 'questions'."
            )
    else:  # pragma: no cover - supported formats only
        raise ValueError("Formato file non supportato. Caricare un file CSV o JSON.")

    if df is None or df.empty:
        raise ValueError("Il file importato è vuoto o non contiene dati validi.")

    if "question" in df.columns and "domanda" not in df.columns:
        df.rename(columns={"question": "domanda"}, inplace=True)
    if "expected_answer" in df.columns and "risposta_attesa" not in df.columns:
        df.rename(columns={"expected_answer": "risposta_attesa"}, inplace=True)

    if not all(col in df.columns for col in REQUIRED_QUESTION_COLUMNS):
        raise ValueError(
            f"Il file importato deve contenere le colonne '{REQUIRED_QUESTION_COLUMNS[0]}' e '{REQUIRED_QUESTION_COLUMNS[1]}'."
        )

    if "id" not in df.columns:
        df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]
    else:
        df["id"] = df["id"].astype(str)

    if "categoria" not in df.columns:
        df["categoria"] = ""
    else:
        df["categoria"] = df["categoria"].astype(str).fillna("")

    df["domanda"] = df["domanda"].astype(str).fillna("")
    df["risposta_attesa"] = df["risposta_attesa"].astype(str).fillna("")

    return df[["id", "domanda", "risposta_attesa", "categoria"]]


def read_question_sets(file: IO[str] | IO[bytes]) -> List[Dict[str, Any]]:
    """Legge un file di set di domande (CSV o JSON) e restituisce una lista di dizionari."""
    if hasattr(file, "seek"):
        file.seek(0)
    file_extension = os.path.splitext(file.name)[1].lower()

    if file_extension == ".csv":
        try:
            df = pd.read_csv(file)
        except Exception as e:  # pragma: no cover - handled via ValueError
            raise ValueError("Il formato del file csv non è valido") from e

        missing = [c for c in REQUIRED_SET_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(
                "Il file CSV deve contenere le colonne " + ", ".join(REQUIRED_SET_COLUMNS)
            )

        sets_dict: Dict[str, List[Dict[str, str]]] = {}
        for _, row in df.iterrows():
            name = str(row["name"]).strip()
            if not name:
                continue
            question = {
                "id": str(row["id"]).strip() if not pd.isna(row["id"]) else "",
                "domanda": str(row["domanda"]).strip()
                if not pd.isna(row["domanda"])
                else "",
                "risposta_attesa": str(row["risposta_attesa"]).strip()
                if not pd.isna(row["risposta_attesa"])
                else "",
                "categoria": str(row["categoria"]).strip()
                if not pd.isna(row["categoria"])
                else "",
            }
            sets_dict.setdefault(name, []).append(question)
        return [{"name": n, "questions": qs} for n, qs in sets_dict.items()]

    elif file_extension == ".json":
        try:
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            data = json.loads(content)
        except Exception as e:  # pragma: no cover - handled via ValueError
            raise ValueError("Il formato del file json non è valido") from e

        if not isinstance(data, list):
            raise ValueError("Il formato del file json non è valido")
        return data

    else:  # pragma: no cover - supported formats only
        raise ValueError("Formato file non supportato. Caricare un file CSV o JSON.")


def read_test_results(file: IO[str] | IO[bytes]) -> pd.DataFrame:
    """Legge un file di risultati di test (CSV o JSON) e restituisce un DataFrame normalizzato."""
    if hasattr(file, "seek"):
        file.seek(0)
    file_extension = os.path.splitext(file.name)[1].lower()

    if file_extension == ".csv":
        try:
            df = pd.read_csv(file)
        except Exception as e:  # pragma: no cover - handled via ValueError
            raise ValueError("Il formato del file csv non è valido") from e
    elif file_extension == ".json":
        try:
            data = json.load(file)
        except Exception as e:  # pragma: no cover - handled via ValueError
            raise ValueError("Il formato del file json non è valido") from e
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            raise ValueError(
                "Il file JSON deve contenere un oggetto o una lista di risultati."
            )
        df = pd.DataFrame(data)
    else:  # pragma: no cover - supported formats only
        raise ValueError("Formato file non supportato. Caricare un file CSV o JSON.")

    if df is None or df.empty:
        raise ValueError("Il file importato è vuoto o non contiene dati validi.")

    if "id" not in df.columns:
        df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]
    else:
        df["id"] = df["id"].astype(str)

    if "set_id" not in df.columns:
        df["set_id"] = ""
    else:
        df["set_id"] = df["set_id"].astype(str).fillna("")

    if "timestamp" not in df.columns:
        df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        df["timestamp"] = df["timestamp"].astype(str).fillna(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def _parse_results(value: Any) -> Dict:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:  # pragma: no cover - invalid json handled as empty dict
                return {}
        if isinstance(value, dict):
            return value
        return {}

    if "results" not in df.columns:
        df["results"] = [{} for _ in range(len(df))]
    else:
        df["results"] = df["results"].apply(_parse_results)

    return df[["id", "set_id", "timestamp", "results"]]
