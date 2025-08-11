import pandas as pd

from models.question import Question
from models.orm_models import QuestionORM
from models.database import DatabaseEngine


def test_add_and_update_question(in_memory_db):
    qid = Question.add('d1', 'r1', 'c1')
    with DatabaseEngine.instance().get_session() as session:
        q = session.get(QuestionORM, qid)
        assert q.domanda == 'd1'
    assert Question.update(qid, domanda='d2', categoria='c2') is True
    with DatabaseEngine.instance().get_session() as session:
        q = session.get(QuestionORM, qid)
        assert q.domanda == 'd2'
        assert q.categoria == 'c2'
    assert Question.update('missing', domanda='x') is False


def test_persist_entities_handles_duplicates(in_memory_db):
    existing_id = Question.add('d', 'r', 'c')
    df = pd.DataFrame([
        {'id': existing_id, 'domanda': 'd', 'risposta_attesa': 'r', 'categoria': 'c'},
        {'id': 'new1', 'domanda': 'd2', 'risposta_attesa': 'r2', 'categoria': 'c2'},
        {'id': 'new1', 'domanda': 'd2', 'risposta_attesa': 'r2', 'categoria': 'c2'},
    ])
    count, warnings = Question._persist_entities(df)
    assert count == 1
    assert len(warnings) == 1
    assert 'già esistente' in warnings[0]
    with DatabaseEngine.instance().get_session() as session:
        assert session.get(QuestionORM, 'new1') is not None
