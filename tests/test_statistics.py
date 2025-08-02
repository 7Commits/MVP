import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from controllers.test_controller import calculate_statistics  # noqa: E402


def test_calculate_statistics():
    results = {
        "q1": {
            "question": "Domanda 1",
            "evaluation": {
                "score": 80,
                "similarity": 70,
                "correctness": 90,
                "completeness": 60,
            },
        },
        "q2": {
            "question": "Domanda 2",
            "evaluation": {
                "score": 60,
                "similarity": 50,
                "correctness": 40,
                "completeness": 80,
            },
        },
    }
    stats = calculate_statistics(results)
    assert stats["avg_score"] == pytest.approx(70.0)
    assert len(stats["per_question_scores"]) == 2
    assert {"question": "Domanda 1", "score": 80} in stats["per_question_scores"]
    assert stats["radar_metrics"]["similarity"] == pytest.approx(60.0)
    assert stats["radar_metrics"]["correctness"] == pytest.approx(65.0)
    assert stats["radar_metrics"]["completeness"] == pytest.approx(70.0)


def test_calculate_statistics_empty():
    stats = calculate_statistics({})
    assert stats["avg_score"] == 0
    assert stats["per_question_scores"] == []
    assert stats["radar_metrics"] == {"similarity": 0, "correctness": 0, "completeness": 0}
