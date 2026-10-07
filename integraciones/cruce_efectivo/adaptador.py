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
            "id": "criterio",
            "etiqueta": "Criterio",
            "tipo": "texto",
            "requerido": True,
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
            "requerido": False,
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

    def validar_parametros(self, parametros):

     errores = []

     criterio = str(
         parametros.get("criterio", "")
     ).strip()

     anio = str(
         parametros.get("anio", "")
     ).strip()

     periodo = str(
         parametros.get("mes", "")
     ).strip()

     if not criterio:
        errores.append(
            "Debe ingresar un criterio."
        )

     return errores

    def ejecutar(self, parametros, reportar_evento):

     try:

        criterio = str(
            parametros.get("criterio", "")
        ).strip()

        anio = str(
            parametros.get("anio", "")
        ).strip()

        periodo = str(
            parametros.get("mes", "")
        ).strip()

        archivo_ctasbanc = str(
            parametros.get(
                "archivo_ctasbanc",
                ""
            )
        ).strip()

        reportar_evento(
            "INICIO",
            f"Iniciando Cruce de Efectivo para criterio {criterio}",
            5,
        )

        if str(self.ruta_proyecto) not in sys.path:
            sys.path.insert(
                0,
                str(self.ruta_proyecto)
            )

        from procesos.proceso_principal import ejecutar

        archivo_generado = ejecutar(
            criterio=criterio,
            anio=anio,
            periodo=periodo,
            archivo_ctasbanc=archivo_ctasbanc,
            reportar_evento=reportar_evento,
        )

        reportar_evento(
            "FINALIZADO",
            "Proceso ejecutado correctamente.",
            100,
        )

        return ResultadoEjecucion(
            exitoso=True,
            estado="FINALIZADO",
            mensaje="Cruce de Efectivo ejecutado correctamente.",
            archivos_generados=[
                str(archivo_generado)
            ] if archivo_generado else [],
            carpeta_salida=str(
                Path(archivo_generado).parent
            ) if archivo_generado else None,
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