import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from views import home


class DummyColumn:
    def __init__(self, parent):
        self.parent = parent

    def markdown(self, text, **kwargs):
        self.parent.markdown(text, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class DummySt:
    def __init__(self):
        self.markdown_calls = []

    def markdown(self, text, **kwargs):
        self.markdown_calls.append(text)

    def columns(self, n):
        return (DummyColumn(self), DummyColumn(self))


def test_home_render_injects_styles_and_content(monkeypatch):
    dummy_st = DummySt()
    monkeypatch.setattr(home, 'st', dummy_st)

    called = {'home_styles': False}

    def fake_add_home_styles():
        called['home_styles'] = True

    monkeypatch.setattr(home, 'add_home_styles', fake_add_home_styles)

    home.render()

    assert called['home_styles'] is True
    assert any('Piattaforma di Valutazione LLM' in m for m in dummy_st.markdown_calls)
