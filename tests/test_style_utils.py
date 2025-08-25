import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from views import style_utils


class DummySt:
    def __init__(self):
        self.calls = []

    def markdown(self, text, **kwargs):
        self.calls.append(text)


def test_add_global_styles_injects_css(monkeypatch):
    dummy_st = DummySt()
    monkeypatch.setattr(style_utils, 'st', dummy_st)

    style_utils.add_global_styles()

    assert any('stTextInput' in c for c in dummy_st.calls)


def test_add_page_header_calls_global_styles_and_renders(monkeypatch):
    dummy_st = DummySt()
    monkeypatch.setattr(style_utils, 'st', dummy_st)
    called = {'css': False}

    def fake_load_css():
        called['css'] = True

    monkeypatch.setattr(style_utils, 'load_css', fake_load_css)

    style_utils.add_page_header('Titolo', icon='✨', description='desc')

    assert called['css'] is True
    assert any('✨ Titolo' in c and 'desc' in c for c in dummy_st.calls)


def test_add_section_title_renders_text(monkeypatch):
    dummy_st = DummySt()
    monkeypatch.setattr(style_utils, 'st', dummy_st)

    style_utils.add_section_title('Section', icon='➡')

    assert any('➡ Section' in c for c in dummy_st.calls)


def test_add_home_styles_injects_css(monkeypatch):
    dummy_st = DummySt()
    monkeypatch.setattr(style_utils, 'st', dummy_st)

    style_utils.add_home_styles()

    assert any('feature-box' in c for c in dummy_st.calls)
