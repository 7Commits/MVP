import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.cache import (  # noqa: E402
    get_questions,
    refresh_questions,
    get_question_sets,
    refresh_question_sets,
    get_api_presets,
    refresh_api_presets,
    get_results,
    refresh_results,
)
from models.question import Question  # noqa: E402
from models.question_set import QuestionSet  # noqa: E402
from models.api_preset import APIPreset  # noqa: E402
from models.test_result import TestResult  # noqa: E402


def test_get_questions_cache(monkeypatch):
    call_count = {"count": 0}

    def fake_load_all():
        call_count["count"] += 1
        return [
            Question(id="1", domanda="Q1", risposta_attesa="A1", categoria="C1")
        ]

    monkeypatch.setattr(Question, "load_all", staticmethod(fake_load_all))
    get_questions.cache_clear()

    df1 = get_questions()
    assert call_count["count"] == 1
    assert list(df1["id"]) == ["1"]

    df2 = get_questions()
    assert call_count["count"] == 1
    assert df2.equals(df1)

    def fake_load_all_new():
        call_count["count"] += 1
        return [
            Question(id="2", domanda="Q2", risposta_attesa="A2", categoria="C2")
        ]

    monkeypatch.setattr(Question, "load_all", staticmethod(fake_load_all_new))
    df3 = refresh_questions()
    assert call_count["count"] == 2
    assert list(df3["id"]) == ["2"]

    df4 = get_questions()
    assert call_count["count"] == 2
    assert df4.equals(df3)


def test_get_question_sets_cache(monkeypatch):
    call_count = {"count": 0}

    def fake_load_all():
        call_count["count"] += 1
        return [
            QuestionSet(id="1", name="S1", questions=["q1"])
        ]

    monkeypatch.setattr(QuestionSet, "load_all", staticmethod(fake_load_all))
    get_question_sets.cache_clear()

    df1 = get_question_sets()
    assert call_count["count"] == 1
    assert list(df1["id"]) == ["1"]

    df2 = get_question_sets()
    assert call_count["count"] == 1
    assert df2.equals(df1)

    def fake_load_all_new():
        call_count["count"] += 1
        return [
            QuestionSet(id="2", name="S2", questions=["q2"])
        ]

    monkeypatch.setattr(QuestionSet, "load_all", staticmethod(fake_load_all_new))
    df3 = refresh_question_sets()
    assert call_count["count"] == 2
    assert list(df3["id"]) == ["2"]

    df4 = get_question_sets()
    assert call_count["count"] == 2
    assert df4.equals(df3)


def test_get_api_presets_cache(monkeypatch):
    call_count = {"count": 0}

    def fake_load_all():
        call_count["count"] += 1
        return [
            APIPreset(
                id="1",
                name="P1",
                provider_name="prov",
                endpoint="e1",
                api_key="k1",
                model="m1",
                temperature=0.5,
                max_tokens=10,
            )
        ]

    monkeypatch.setattr(APIPreset, "load_all", staticmethod(fake_load_all))
    get_api_presets.cache_clear()

    df1 = get_api_presets()
    assert call_count["count"] == 1
    assert list(df1["id"]) == ["1"]

    df2 = get_api_presets()
    assert call_count["count"] == 1
    assert df2.equals(df1)

    def fake_load_all_new():
        call_count["count"] += 1
        return [
            APIPreset(
                id="2",
                name="P2",
                provider_name="prov2",
                endpoint="e2",
                api_key="k2",
                model="m2",
                temperature=0.7,
                max_tokens=20,
            )
        ]

    monkeypatch.setattr(APIPreset, "load_all", staticmethod(fake_load_all_new))
    df3 = refresh_api_presets()
    assert call_count["count"] == 2
    assert list(df3["id"]) == ["2"]

    df4 = get_api_presets()
    assert call_count["count"] == 2
    assert df4.equals(df3)


def test_get_and_refresh_results(monkeypatch):
    load_called = {"count": 0}
    refresh_called = {"count": 0}
    df1 = pd.DataFrame([{"id": "1", "set_id": "s1", "timestamp": "t1", "results": {}}])
    df2 = pd.DataFrame([{"id": "2", "set_id": "s2", "timestamp": "t2", "results": {}}])

    def fake_load_all_df():
        load_called["count"] += 1
        return df1

    def fake_refresh_cache():
        refresh_called["count"] += 1
        return df2

    monkeypatch.setattr(TestResult, "load_all_df", staticmethod(fake_load_all_df))
    monkeypatch.setattr(TestResult, "refresh_cache", staticmethod(fake_refresh_cache))

    assert get_results().equals(df1)
    assert load_called["count"] == 1

    assert refresh_results().equals(df2)
    assert refresh_called["count"] == 1
