from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List

ReportadorEvento = Callable[[str, str, int], None]


class ContratoProyecto(ABC):
    """Contrato que debe implementar cada proyecto integrado."""

    @abstractmethod
    def obtener_metadatos(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def obtener_campos_configuracion(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def validar_disponibilidad(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def validar_parametros(self, parametros: Dict[str, Any]) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def ejecutar(
        self,
        parametros: Dict[str, Any],
        reportar_evento: ReportadorEvento,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def cancelar(self) -> None:
        """Punto de extensión para módulos que admitan cancelación."""
        return None
