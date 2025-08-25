import pandas as pd

from models.question import Question
from models.question_set import QuestionSet
from models.orm_models import QuestionSetORM
from models.database import DatabaseEngine


def test_create_and_update_question_set(in_memory_db):
    qid1 = Question.add('d1', 'r1')
    qid2 = Question.add('d2', 'r2')
    set_id = QuestionSet.create('set1', [qid1])
    with DatabaseEngine.instance().get_session() as session:
        qset = session.get(QuestionSetORM, set_id)
        assert qset.name == 'set1'
        assert [q.id for q in qset.questions] == [qid1]
    QuestionSet.update(set_id, name='set2', question_ids=[qid2])
    with DatabaseEngine.instance().get_session() as session:
        qset = session.get(QuestionSetORM, set_id)
        assert qset.name == 'set2'
        assert [q.id for q in qset.questions] == [qid2]
    # update of missing set should not raise
    QuestionSet.update('missing', name='x')


def test_resolve_question_ids(monkeypatch, in_memory_db):
    current_questions = pd.DataFrame([
        {'id': '1', 'domanda': 'd1', 'risposta_attesa': 'r1', 'categoria': ''}
    ])
    data = ['1', {'id': '2', 'domanda': 'd2', 'risposta_attesa': 'r2', 'categoria': ''}, {'id': '3'}]
    monkeypatch.setattr(
        'controllers.question_controller.add_question_if_not_exists',
        lambda **kwargs: True,
    )
    ids, updated, new_added, existing_found, warnings = QuestionSet._resolve_question_ids(
        data, current_questions
    )
    assert ids == ['1', '2']
    assert new_added == 1
    assert existing_found == 1
    assert len(warnings) == 1
    assert 'saltata' in warnings[0]
    assert '2' in updated['id'].values
