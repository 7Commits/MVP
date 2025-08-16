import importlib
import sys
import types
from pathlib import Path


def test_app_page_config_and_navigation(monkeypatch):
    """Test di base per la configurazione dell'app Streamlit e l'impostazione della navigazione."""
    # Registra le chiamate all'API di Streamlit
    page_config = {}
    radio_call = {}

    def fake_set_page_config(**kwargs):
        page_config.update(kwargs)

    def fake_radio(label, options):
        radio_call["label"] = label
        radio_call["options"] = options
        return options[0]

    fake_sidebar = types.SimpleNamespace(radio=fake_radio)
    fake_st = types.SimpleNamespace(
        set_page_config=fake_set_page_config,
        sidebar=fake_sidebar,
        title=lambda *a, **k: None,
    )

    monkeypatch.setitem(sys.modules, "streamlit", fake_st)

    # Assicura che la radice del repository sia importabile
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

    # Crea moduli di vista fittizi richiesti da app.py
    views_pkg = types.ModuleType("views")
    views_pkg.__path__ = []  # contrassegna come pacchetto
    view_names = [
        "api_configurazione",
        "esecuzione_test",
        "gestione_domande",
        "gestione_set",
        "home",
        "visualizza_risultati",
    ]
    for name in view_names:
        mod = types.ModuleType(f"views.{name}")
        mod.render = lambda: None
        sys.modules[f"views.{name}"] = mod
        setattr(views_pkg, name, mod)

    views_pkg.page_registry = {
        "Home": views_pkg.home.render,
        "Configurazione API": views_pkg.api_configurazione.render,
        "Gestione Domande": views_pkg.gestione_domande.render,
        "Gestione Set di Domande": views_pkg.gestione_set.render,
        "Esecuzione Test": views_pkg.esecuzione_test.render,
        "Visualizzazione Risultati": views_pkg.visualizza_risultati.render,
    }

    session_state_mod = types.ModuleType("views.session_state")
    session_state_mod.initialize_session_state = lambda: None
    sys.modules["views.session_state"] = session_state_mod

    style_utils_mod = types.ModuleType("views.style_utils")
    style_utils_mod.add_global_styles = lambda: None
    sys.modules["views.style_utils"] = style_utils_mod

    sys.modules["views"] = views_pkg

    # Assicura un'importazione pulita di app
    monkeypatch.delitem(sys.modules, "app", raising=False)
    app = importlib.import_module("app")

    assert page_config["page_title"] == "LLM Test Evaluation Platform"
    assert radio_call["label"] == "Navigazione"
    assert radio_call["options"] == list(app.PAGES.keys())

