import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from views import component_utils


class DummySt:
    def __init__(self):
        self.calls = []

    def markdown(self, text, **kwargs):
        self.calls.append(text)


def test_create_card_renders_expected_html(monkeypatch):
    dummy_st = DummySt()
    monkeypatch.setattr(component_utils, 'st', dummy_st)

    component_utils.create_card('Titolo', 'Contenuto', icon='⭐', is_success=True)

    assert any('Titolo' in c and 'Contenuto' in c and '⭐' in c for c in dummy_st.calls)
    # success card should have specific background color
    assert any('#f8fff9' in c for c in dummy_st.calls)


def test_create_metrics_container_renders_metrics(monkeypatch):
    dummy_st = DummySt()
    monkeypatch.setattr(component_utils, 'st', dummy_st)

    metrics = [{'label': 'Accuracy', 'value': 95, 'unit': '%', 'icon': '📈'}]
    component_utils.create_metrics_container(metrics)

    # first call is CSS, second call is metrics HTML
    assert len(dummy_st.calls) >= 2
    metrics_html = dummy_st.calls[-1]
    assert 'Accuracy' in metrics_html
    assert '95' in metrics_html
    assert '📈' in metrics_html
