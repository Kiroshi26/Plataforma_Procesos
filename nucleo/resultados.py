from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class ResultadoEjecucion:
    exitoso: bool
    estado: str
    mensaje: str
    archivos_generados: List[str] = field(default_factory=list)
    carpeta_salida: str = ""
    advertencias: List[str] = field(default_factory=list)
    errores: List[str] = field(default_factory=list)
    metricas: Dict[str, Any] = field(default_factory=dict)

    def como_diccionario(self) -> Dict[str, Any]:
        return asdict(self)
