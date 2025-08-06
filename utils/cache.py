from functools import lru_cache
from dataclasses import asdict
import pandas as pd

from models.question import Question
from models.question_set import QuestionSet
from models.api_preset import APIPreset
from models.test_result import TestResult


@lru_cache(maxsize=1)
def get_questions() -> pd.DataFrame:
    data = [asdict(q) for q in Question.load_all()]
    columns = ["id", "domanda", "risposta_attesa", "categoria"]
    return pd.DataFrame(data, columns=columns)


def refresh_questions() -> pd.DataFrame:
    get_questions.cache_clear()
    return get_questions()


@lru_cache(maxsize=1)
def get_question_sets() -> pd.DataFrame:
    data = [asdict(s) for s in QuestionSet.load_all()]
    columns = ["id", "name", "questions"]
    return pd.DataFrame(data, columns=columns)


def refresh_question_sets() -> pd.DataFrame:
    get_question_sets.cache_clear()
    return get_question_sets()


@lru_cache(maxsize=1)
def get_api_presets() -> pd.DataFrame:
    data = [asdict(p) for p in APIPreset.load_all()]
    columns = [
        "id",
        "name",
        "provider_name",
        "endpoint",
        "api_key",
        "model",
        "temperature",
        "max_tokens",
    ]
    return pd.DataFrame(data, columns=columns)


def refresh_api_presets() -> pd.DataFrame:
    get_api_presets.cache_clear()
    return get_api_presets()


@lru_cache(maxsize=1)
def get_results() -> pd.DataFrame:
    data = [asdict(r) for r in TestResult.load_all()]
    columns = ["id", "set_id", "timestamp", "results"]
    return pd.DataFrame(data, columns=columns)


def refresh_results() -> pd.DataFrame:
    get_results.cache_clear()
    return get_results()
