from typing import Any, Dict

from nucleo.contrato_proyecto import ContratoProyecto, ReportadorEvento
from nucleo.resultados import ResultadoEjecucion


def ejecutar_proyecto(
    proyecto: ContratoProyecto,
    parametros: Dict[str, Any],
    reportar_evento: ReportadorEvento,
) -> Dict[str, Any]:
    disponibilidad = proyecto.validar_disponibilidad()
    if not disponibilidad.get("disponible", False):
        return ResultadoEjecucion(
            exitoso=False,
            estado="NO DISPONIBLE",
            mensaje=disponibilidad.get("mensaje", "Módulo no disponible."),
        ).como_diccionario()

    errores = proyecto.validar_parametros(parametros)
    if errores:
        return ResultadoEjecucion(
            exitoso=False,
            estado="PARAMETROS INVALIDOS",
            mensaje="Revise los parámetros antes de ejecutar.",
            errores=errores,
        ).como_diccionario()

    return proyecto.ejecutar(parametros, reportar_evento)
