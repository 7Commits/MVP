from controllers import question_controller, question_set_controller


def test_create_update_delete_set():
    qid1 = question_controller.add_question("Q1", "A1")
    qid2 = question_controller.add_question("Q2", "A2")

    set_id = question_set_controller.create_set("Set1", [qid1, qid2])
    sets = question_set_controller.load_sets()
    row = sets[sets["id"] == set_id].iloc[0]
    assert row["name"] == "Set1"
    assert set(row["questions"]) == {qid1, qid2}

    question_set_controller.update_set(set_id, name="Set2", question_ids=[qid2])
    sets2 = question_set_controller.load_sets()
    row2 = sets2[sets2["id"] == set_id].iloc[0]
    assert row2["name"] == "Set2"
    assert row2["questions"] == [qid2]

    question_set_controller.delete_set(set_id)
    sets3 = question_set_controller.load_sets()
    assert set_id not in sets3["id"].values
