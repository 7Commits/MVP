import models.cached_data as cached_data


def test_get_questions(monkeypatch):
    called = {}

    def fake_load_all():
        called['done'] = True
        return [1]

    monkeypatch.setattr(cached_data.Question, 'load_all', staticmethod(fake_load_all))
    assert cached_data.get_questions() == [1]
    assert called


def test_get_question_sets(monkeypatch):
    called = {}

    def fake_load_all():
        called['done'] = True
        return ['set']

    monkeypatch.setattr(cached_data.QuestionSet, 'load_all', staticmethod(fake_load_all))
    assert cached_data.get_question_sets() == ['set']
    assert called


def test_get_api_presets(monkeypatch):
    called = {}

    def fake_load_all():
        called['done'] = True
        return ['preset']

    monkeypatch.setattr(cached_data.APIPreset, 'load_all', staticmethod(fake_load_all))
    assert cached_data.get_api_presets() == ['preset']
    assert called


def test_get_results(monkeypatch):
    called = {}

    def fake_load_all():
        called['done'] = True
        return ['result']

    monkeypatch.setattr(cached_data.TestResult, 'load_all', staticmethod(fake_load_all))
    assert cached_data.get_results() == ['result']
    assert called
