from pathlib import Path
import subprocess

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
                "Cruce automático de movimientos de efectivo "
                "a partir de los soportes PDF."
            ),
            "estado": "DISPONIBLE",
        }

    def obtener_campos_configuracion(self):
        return []

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
        return []

    def ejecutar(self, parametros, reportar_evento):
        try:
            reportar_evento(
                "INICIO",
                "Abriendo aplicación de Cruce Efectivo.",
                10,
            )

            app = self.ruta_proyecto / "app.py"

            subprocess.Popen(
                ["python", str(app)],
                cwd=str(self.ruta_proyecto),
            )

            reportar_evento(
                "FINALIZADO",
                "Aplicación abierta correctamente.",
                100,
            )

            return ResultadoEjecucion(
                exitoso=True,
                estado="FINALIZADO",
                mensaje="Cruce Efectivo iniciado correctamente.",
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