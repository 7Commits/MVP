"""Template base per l'esportazione di dati su file."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, IO, Union, final


class ExportTemplate(ABC):
    """Classe base astratta per implementare l'esportazione su file."""

    @abstractmethod
    def gather_data(self) -> Any:
        """Raccoglie i dati correnti da esportare."""
        pass

    @final
    def export_to_file(self, destination: Union[str, IO[Any]]) -> None:
        """Esporta i dati raccolti su ``destination``.

        Nota: le sottoclassi non devono sovrascrivere questo metodo.

        Parameters
        ----------
        destination: Union[str, IO[Any]]
            Percorso del file di destinazione oppure file aperto in scrittura.
        """
        from utils.file_writer_utils import write_dataset

        data = self.gather_data()
        write_dataset(data, destination)


__all__ = ["ExportTemplate"]
