from pathlib import Path
from typing import Any, Dict, List

from nucleo.contrato_proyecto import (
    ContratoProyecto,
    ReportadorEvento,
)
from nucleo.resultados import ResultadoEjecucion
from nucleo.seguridad_salidas import (
    bloquear_publicacion_corporativa,
    validar_salida_local,
)


class AdaptadorInversiones(ContratoProyecto):

    def __init__(self, ruta_proyecto: str) -> None:
        self.ruta_proyecto = Path(ruta_proyecto)

    def obtener_metadatos(self) -> Dict[str, Any]:
        return {
            "id": "inversiones",
            "nombre": "Inversiones",
            "descripcion": "Procesamiento de inversiones.",
            "estado": "DISPONIBLE",
        }

    def obtener_campos_configuracion(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "periodo",
                "etiqueta": "Periodo",
                "tipo": "periodo",
                "requerido": True,
            },
            {
                "id": "carpeta_salida",
                "etiqueta": "Carpeta local de salida",
                "tipo": "carpeta",
                "requerido": True,
            },
            {
                "id": "publicar_corporativo",
                "etiqueta": "Publicar corporativamente",
                "tipo": "booleano",
                "requerido": False,
                "bloqueado": True,
            },
        ]

    def validar_disponibilidad(self):
        if not self.ruta_proyecto.exists():
            return {
                "disponible": False,
                "mensaje": (
                    f"No existe el proyecto de Inversiones: "
                    f"{self.ruta_proyecto}"
                ),
            }

        if not self.ruta_proyecto.is_dir():
            return {
                "disponible": False,
                "mensaje": (
                    f"La ruta de Inversiones no es una carpeta: "
                    f"{self.ruta_proyecto}"
                ),
            }

        carpeta_src = self.ruta_proyecto / "src"

        if not carpeta_src.exists():
            return {
                "disponible": False,
                "mensaje": (
                    f"No se encontró la carpeta src del proyecto: "
                    f"{carpeta_src}"
                ),
            }

        motor = carpeta_src / "proceso_inversiones.py"

        if not motor.exists():
            return {
                "disponible": False,
                "mensaje": (
                    f"No se encontró el motor de Inversiones: "
                    f"{motor}"
                ),
            }

        return {
            "disponible": True,
            "mensaje": "Motor de Inversiones disponible.",
        }

    def validar_parametros(self, parametros):
        errores = []

        periodo = str(
            parametros.get("periodo", "")
        ).strip()

        if len(periodo) != 7 or periodo[4:5] != "-":
            errores.append(
                "El periodo debe tener formato AAAA-MM."
            )

        return errores

    def ejecutar(
        self,
        parametros: Dict[str, Any],
        reportar_evento: ReportadorEvento,
    ) -> Dict[str, Any]:

        try:
            from integraciones.inversiones.proceso import (
                ejecutar as ejecutar_inversiones,
            )

            periodo = str(
                parametros["periodo"]
            ).strip()

            anio_texto, mes_texto = periodo.split("-")

            anio = int(anio_texto)
            mes = int(mes_texto)

            reportar_evento(
                "INICIO",
                "Preparando proceso de inversiones.",
                5,
            )

            resultado = ejecutar_inversiones(
                configuracion={
                    "carpeta_salida": str(
                        parametros["carpeta_salida"]
                    ),
                },
                anio=anio,
                mes=mes,
                usuario="",
                clave="",
            )

            reportar_evento(
                "FINALIZADO",
                "Proceso ejecutado correctamente.",
                100,
            )

            return ResultadoEjecucion(
                exitoso=resultado.exitoso,
                estado="FINALIZADO",
                mensaje="Proceso ejecutado correctamente.",
                archivos_generados=[
                    str(resultado.archivo_saldos)
                ],
                carpeta_salida=str(
                    parametros["carpeta_salida"]
                ),
                metricas={
                    "periodo": resultado.periodo,
                    "cantidad_saldos": resultado.cantidad_saldos,
                    "cantidad_baseneg": resultado.cantidad_baseneg,
                    "total_mes": resultado.total_mes,
                },
            ).como_diccionario()

        except Exception as error:
            reportar_evento(
                "ERROR",
                str(error),
                100,
            )

            return ResultadoEjecucion(
                exitoso=False,
                estado="ERROR",
                mensaje=str(error),
                errores=[
                    str(error)
                ],
            ).como_diccionario()