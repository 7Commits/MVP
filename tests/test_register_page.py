import pytest

from views import register_page, page_registry


def test_register_page_prevents_duplicates():
    page_registry.clear()

    @register_page("Example")
    def first():
        return "first"

    assert page_registry["Example"] is first

    with pytest.raises(ValueError):
        @register_page("Example")
        def second():  # pragma: no cover - funzione non registrata
            return "second"

    assert page_registry["Example"] is first
