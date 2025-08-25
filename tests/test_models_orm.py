from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models.orm_models import (
    Base,
    QuestionORM,
    QuestionSetORM,
    TestResultORM as ResultORM,
    APIPresetORM,
    question_set_questions,
)


def test_orm_tables_and_relationships():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        question = QuestionORM(
            id="q1",
            domanda="2+2?",
            risposta_attesa="4",
            categoria="math",
        )
        qset = QuestionSetORM(id="s1", name="Sample Set", questions=[question])
        result = ResultORM(
            id="r1",
            set_id="s1",
            timestamp="2024-01-01T00:00:00",
            results={"q1": "4"},
        )
        preset = APIPresetORM(
            id="a1",
            name="default",
            provider_name="openai",
            endpoint="http://api.example",
            api_key="secret",
            model="gpt",
            temperature=0.1,
            max_tokens=10,
        )
        session.add_all([qset, result, preset])
        session.commit()

        assert session.get(QuestionORM, "q1").domanda == "2+2?"
        assert session.get(QuestionSetORM, "s1").questions[0].id == "q1"
        assert session.get(ResultORM, "r1").results == {"q1": "4"}
        assert session.get(APIPresetORM, "a1").model == "gpt"

    # Column names
    assert set(QuestionORM.__table__.columns.keys()) == {
        "id",
        "domanda",
        "risposta_attesa",
        "categoria",
    }
    assert set(QuestionSetORM.__table__.columns.keys()) == {"id", "name"}
    assert set(ResultORM.__table__.columns.keys()) == {
        "id",
        "set_id",
        "timestamp",
        "results",
    }
    assert set(APIPresetORM.__table__.columns.keys()) == {
        "id",
        "name",
        "provider_name",
        "endpoint",
        "api_key",
        "model",
        "temperature",
        "max_tokens",
    }
    assert set(question_set_questions.c.keys()) == {"set_id", "question_id"}

    # Foreign keys
    fk_set = list(question_set_questions.c.set_id.foreign_keys)[0]
    fk_question = list(question_set_questions.c.question_id.foreign_keys)[0]
    assert fk_set.column.table.name == "question_sets"
    assert fk_question.column.table.name == "questions"

    # Metadata consistency
    for name, table in [
        ("questions", QuestionORM.__table__),
        ("question_sets", QuestionSetORM.__table__),
        ("test_results", ResultORM.__table__),
        ("api_presets", APIPresetORM.__table__),
        ("question_set_questions", question_set_questions),
    ]:
        assert name in Base.metadata.tables
        assert Base.metadata.tables[name] is table

