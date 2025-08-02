from functools import lru_cache
import pandas as pd

from models.question import Question
from models.question_set import QuestionSet
from models.api_preset import APIPreset
from models.test_result import TestResult


@lru_cache(maxsize=1)
def get_questions() -> pd.DataFrame:
    return Question.load_all()


def refresh_questions() -> pd.DataFrame:
    get_questions.cache_clear()
    return get_questions()


@lru_cache(maxsize=1)
def get_question_sets() -> pd.DataFrame:
    return QuestionSet.load_all()


def refresh_question_sets() -> pd.DataFrame:
    get_question_sets.cache_clear()
    return get_question_sets()


@lru_cache(maxsize=1)
def get_api_presets() -> pd.DataFrame:
    return APIPreset.load_all()


def refresh_api_presets() -> pd.DataFrame:
    get_api_presets.cache_clear()
    return get_api_presets()


@lru_cache(maxsize=1)
def get_results() -> pd.DataFrame:
    return TestResult.load_all()


def refresh_results() -> pd.DataFrame:
    get_results.cache_clear()
    return get_results()
