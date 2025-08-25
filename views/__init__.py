"""Pacchetto delle viste."""

import logging
from typing import Callable, Dict

logger = logging.getLogger(__name__)


page_registry: Dict[str, Callable] = {}


def register_page(name: str):
    """Decoratore per registrare la funzione di rendering di una pagina."""

    def decorator(func: Callable) -> Callable:
        if name in page_registry:
            messaggio = f"La pagina '{name}' è già registrata"
            logger.warning(messaggio)
            raise ValueError(messaggio)
        page_registry[name] = func
        return func

    return decorator
