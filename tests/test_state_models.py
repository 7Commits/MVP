import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from views.state_models import SetPageState, QuestionPageState


def test_set_page_state_defaults_and_mutability():
    state = SetPageState()
    assert state.save_set_success is False
    assert state.save_set_success_message == 'Set aggiornato con successo!'
    state.save_set_success = True
    assert state.save_set_success is True


def test_question_page_state_defaults_and_mutability():
    state = QuestionPageState()
    assert state.save_success is False
    assert state.delete_success_message == 'Domanda eliminata con successo!'
    state.save_success = True
    assert state.save_success is True
