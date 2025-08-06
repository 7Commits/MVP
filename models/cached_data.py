import logging

from models.api_preset import APIPreset
from models.question import Question
from models.question_set import QuestionSet
from models.test_result import TestResult
logger = logging.getLogger(__name__)


def get_questions():
    return Question.load_all()


def get_question_sets():
    return QuestionSet.load_all()


def get_api_presets():
    return APIPreset.load_all()


def get_results():
    return TestResult.load_all()
