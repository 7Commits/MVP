import pandas as pd

from utils.data_format_utils import build_questions_detail, format_questions_for_view


def test_format_questions_for_view_no_category():
    df = pd.DataFrame(
        {
            "id": ["1"],
            "domanda": ["d1"],
            "risposta_attesa": ["a1"],
        }
    )
    norm_df, question_map, categories = format_questions_for_view(df)

    assert "categoria" in norm_df.columns
    assert norm_df.iloc[0]["categoria"] == "N/A"
    assert categories == ["N/A"]
    assert question_map == {"1": {"domanda": "d1", "categoria": "N/A"}}


def test_format_questions_for_view_empty_df():
    df = pd.DataFrame()
    norm_df, question_map, categories = format_questions_for_view(df)

    assert list(norm_df.columns) == ["id", "domanda", "risposta_attesa", "categoria"]
    assert norm_df.empty
    assert question_map == {}
    assert categories == []


def test_build_questions_detail():
    question_map = {"1": {"domanda": "d1", "categoria": "A"}}
    details = build_questions_detail(question_map, ["1", "2"])
    assert details == [
        {"id": "1", "domanda": "d1", "categoria": "A"},
        {"id": "2", "domanda": "", "categoria": "N/A"},
    ]
    assert build_questions_detail(question_map, "notalist") == []
