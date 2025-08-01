from controllers import question_controller


def test_add_update_delete_question():
    qid = question_controller.add_question("Domanda?", "Risposta", "cat")
    df = question_controller.load_questions()
    assert qid in df["id"].values

    question_controller.update_question(qid, domanda="Nuova domanda", risposta_attesa="Nuova", categoria="newcat")
    df2 = question_controller.load_questions()
    row = df2[df2["id"] == qid].iloc[0]
    assert row["domanda"] == "Nuova domanda"
    assert row["risposta_attesa"] == "Nuova"
    assert row["categoria"] == "newcat"

    question_controller.delete_question(qid)
    df3 = question_controller.load_questions()
    assert qid not in df3["id"].values
