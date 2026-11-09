from pathlib import Path
import sys

from nucleo.contrato_proyecto import ContratoProyecto
from nucleo.resultados import ResultadoEjecucion


class AdaptadorCruceEfectivo(ContratoProyecto):

    def __init__(self, ruta_proyecto):
        self.ruta_proyecto = Path(ruta_proyecto)

    def obtener_metadatos(self):

        return {
            "id": "cruce_efectivo",
            "nombre": "Cruce de Efectivo",
            "descripcion": (
                "Cruce automático de movimientos "
                "de efectivo a partir de soportes PDF."
            ),
            "estado": "DISPONIBLE",
        }

    def obtener_campos_configuracion(self):

        return [
            {
                "id": "modo",
                "etiqueta": "Modo de ejecución",
                "tipo": "lista",
                "opciones": [
                    "INDIVIDUAL",
                    "MASIVO"
                ],
                "requerido": True,
            },
            {
                "id": "criterio",
                "etiqueta": "Criterio",
                "tipo": "texto",
                "requerido": False,
            },
            {
                "id": "anio",
                "etiqueta": "Año",
                "tipo": "anio",
                "requerido": False,
            },
            {
                "id": "mes",
                "etiqueta": "Mes",
                "tipo": "mes_carpeta",
                "requerido": False,
            },
            {
                "id": "archivo_ctasbanc",
                "etiqueta": "Archivo cuentas bancarias",
                "tipo": "archivo_excel",
                "requerido": True,
            },
        ]

    def validar_disponibilidad(self):

        if not self.ruta_proyecto.exists():

            return {
                "disponible": False,
                "mensaje": (
                    f"No existe el proyecto: "
                    f"{self.ruta_proyecto}"
                ),
            }

        app = self.ruta_proyecto / "app.py"

        if not app.exists():

            return {
                "disponible": False,
                "mensaje": (
                    f"No existe app.py en: "
                    f"{self.ruta_proyecto}"
                ),
            }

        return {
            "disponible": True,
            "mensaje": "Proyecto disponible.",
        }

    def validar_parametros(
        self,
        parametros
    ):

        errores = []

        modo = str(
            parametros.get(
                "modo",
                "INDIVIDUAL"
            )
        ).upper()

        criterio = str(
            parametros.get(
                "criterio",
                ""
            )
        ).strip()

        archivo_ctasbanc = str(
            parametros.get(
                "archivo_ctasbanc",
                ""
            )
        ).strip()

        if (
            modo == "INDIVIDUAL"
            and not criterio
        ):

            errores.append(
                "Debe ingresar un criterio."
            )

        if not archivo_ctasbanc:

            errores.append(
                "Debe seleccionar el archivo CTASBANC."
            )

        return errores

    def ejecutar(
        self,
        parametros,
        reportar_evento
    ):

        try:

            modo = str(
                parametros.get(
                    "modo",
                    "INDIVIDUAL"
                )
            ).upper()

            criterio = str(
                parametros.get(
                    "criterio",
                    ""
                )
            ).strip()

            anio = str(
                parametros.get(
                    "anio",
                    ""
                )
            ).strip()

            periodo = str(
                parametros.get(
                    "mes",
                    ""
                )
            ).strip()

            archivo_ctasbanc = str(
                parametros.get(
                    "archivo_ctasbanc",
                    ""
                )
            ).strip()

            reportar_evento(
                "INICIO",
                (
                    f"Iniciando Cruce de Efectivo "
                    f"modo {modo}"
                ),
                5,
            )

            if str(self.ruta_proyecto) not in sys.path:

                sys.path.insert(
                    0,
                    str(self.ruta_proyecto)
                )

            archivos_generados = []

            if modo == "MASIVO":

                from procesos.proceso_masivo import (
                    ejecutar_masivo
                )

                resultado = ejecutar_masivo(
                    anio=anio,
                    periodo=periodo,
                    archivo_ctasbanc=archivo_ctasbanc,
                    reportar_evento=reportar_evento,
                )

                if resultado:
                    archivos_generados = resultado

            else:

                from procesos.proceso_principal import (
                    ejecutar
                )

                archivo_generado = ejecutar(
                    criterio=criterio,
                    anio=anio,
                    periodo=periodo,
                    archivo_ctasbanc=archivo_ctasbanc,
                    reportar_evento=reportar_evento,
                )

                if archivo_generado:
                    archivos_generados = [
                        str(archivo_generado)
                    ]

            reportar_evento(
                "FINALIZADO",
                "Proceso ejecutado correctamente.",
                100,
            )

            carpeta_salida = None

            if archivos_generados:
                carpeta_salida = str(
                    Path(
                        archivos_generados[0]
                    ).parent
                )

            return ResultadoEjecucion(
                exitoso=True,
                estado="FINALIZADO",
                mensaje="Cruce de Efectivo ejecutado correctamente.",
                archivos_generados=archivos_generados,
                carpeta_salida=carpeta_salida,
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
                errores=[str(error)],
            ).como_diccionario()