from models.openai_service import (
    evaluate_answer as _evaluate_answer,
    generate_example_answer_with_llm as _generate_example_answer_with_llm,
    test_api_connection as _test_api_connection,
    DEFAULT_MODEL,
    DEFAULT_ENDPOINT,
)


def evaluate_answer(question: str, expected_answer: str, actual_answer: str,
                    client_config: dict, show_api_details: bool = False):
    return _evaluate_answer(question, expected_answer, actual_answer,
                            client_config, show_api_details)


def generate_example_answer_with_llm(question: str, client_config: dict,
                                      show_api_details: bool = False):
    return _generate_example_answer_with_llm(question, client_config, show_api_details)


def test_api_connection(api_key: str, endpoint: str, model: str,
                         temperature: float, max_tokens: int):
    return _test_api_connection(api_key, endpoint, model, temperature, max_tokens)

