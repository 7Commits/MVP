import pandas as pd

from models.test_result import TestResult
from models.orm_models import TestResultORM
from models.database import DatabaseEngine


def test_add_and_persist_entities(in_memory_db):
    TestResult.load_all_df.cache_clear()
    existing_id = TestResult.add('set1', {'timestamp': 't1'})
    TestResult.load_all_df.cache_clear()
    df = pd.DataFrame([
        {'id': existing_id, 'set_id': 'set1', 'timestamp': 't1', 'results': {}},
        {'id': 'new', 'set_id': 'set2', 'timestamp': 't2', 'results': {}},
    ])
    added = TestResult._persist_entities(df)
    assert added == 1
    with DatabaseEngine.instance().get_session() as session:
        assert session.get(TestResultORM, 'new') is not None


def test_calculate_statistics():
    data = {
        'q1': {'question': 'Q1', 'evaluation': {'score': 1, 'similarity': 2, 'correctness': 3, 'completeness': 4}},
        'q2': {'question': 'Q2', 'evaluation': {'score': 3, 'similarity': 6, 'correctness': 9, 'completeness': 12}},
    }
    stats = TestResult.calculate_statistics(data)
    assert stats['avg_score'] == 2
    assert stats['radar_metrics']['similarity'] == 4
    assert len(stats['per_question_scores']) == 2
    assert TestResult.calculate_statistics({}) == {
        'avg_score': 0,
        'per_question_scores': [],
        'radar_metrics': {'similarity': 0, 'correctness': 0, 'completeness': 0},
    }
