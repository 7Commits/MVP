"""Template base per l'importazione di dati da file."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, IO, final

logger = logging.getLogger(__name__)


class ImportTemplate(ABC):
    """Classe base astratta per implementare l'importazione da file.

    Le sottoclassi devono implementare ``parse_file`` e ``persist_data`` mentre
    questo template gestisce il flusso dell'operazione e l'handling degli errori.
    """

    @final
    def import_from_file(self, file: IO[Any]) -> Any:
        """Esegue l'importazione da un file.

        Questo metodo fornisce il flusso standard dell'importazione e **non deve
        essere sovrascritto** dalle sottoclassi.

        Il flusso standard prevede il parsing tramite :meth:`parse_file` seguito
        dalla persistenza dei dati con :meth:`persist_data`.

        Parameters
        ----------
        file: IO[Any]
            File aperto da cui leggere i dati. Non viene chiuso.

        Returns
        -------
        Any
            Il valore restituito da :meth:`persist_data`.

        Raises
        ------
        ValueError
            Se si verifica un errore durante l'importazione. L'eccezione
            originale viene loggata e incapsulata in un ``ValueError``.
        """
        try:
            logger.debug(
                "Avvio importazione dal file %s", getattr(file, "name", "<memory>")
            )
            parsed = self.parse_file(file)
            logger.debug("Parsing completato: %s", parsed)
            result = self.persist_data(parsed)
            logger.info(
                "Importazione completata con successo dal file %s",
                getattr(file, "name", "<memory>"),
            )
            return result
        except Exception as exc:  # noqa: BLE001
            logger.exception("Errore durante l'importazione: %s", exc)
            raise ValueError("Errore durante l'importazione") from exc

    @abstractmethod
    def parse_file(self, file: IO[Any]) -> Any:
        """Legge e interpreta il contenuto di ``file``."""
        pass

    @abstractmethod
    def persist_data(self, parsed: Any) -> Any:
        """Persiste i dati parsati nel database o in altra destinazione."""
        pass


__all__ = ["ImportTemplate"]
