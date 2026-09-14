import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from nucleo.contrato_proyecto import ContratoProyecto, ReportadorEvento
from nucleo.resultados import ResultadoEjecucion
from nucleo.seguridad_salidas import validar_salida_local


class AdaptadorComisiones(ContratoProyecto):
    """Conecta la plataforma con el motor estable de Comisiones."""

    ETAPAS = {
        "PROCESO COMPLETO": 5,
        "1. EJECUTANDO": 12,
        "2. EJECUTANDO": 22,
        "3. EJECUTANDO": 32,
        "4. EJECUTANDO": 42,
        "5. EJECUTANDO": 52,
        "6. EJECUTANDO": 62,
        "7. EJECUTANDO": 72,
        "8. LEYENDO": 80,
        "ESCRIBIENDO": 86,
        "GENERANDO INFORME": 86,
        "APLICANDO FORMATO": 91,
        "APLICANDO ESTILO": 91,
        "VALIDANDO INFORME": 95,
        "INFORME GENERADO": 98,
        "INFORME FINAL GENERADO": 98,
    }

    def __init__(self, ruta_proyecto: str) -> None:
        self.ruta_proyecto = Path(ruta_proyecto)
        self._proceso: Optional[subprocess.Popen] = None
        self._cancelacion_solicitada = False

    def obtener_metadatos(self) -> Dict[str, Any]:
        return {
            "id": "comisiones",
            "nombre": "Comisiones 250115",
            "descripcion": (
                "Procesa las fuentes originales y genera el informe informativo "
                "de conciliación de Comisiones."
            ),
            "estado": "INTEGRADO",
        }

    def obtener_campos_configuracion(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "anio",
                "etiqueta": "Año",
                "tipo": "entero",
                "requerido": True,
            },
            {
                "id": "mes",
                "etiqueta": "Mes",
                "tipo": "mes",
                "requerido": True,
            },
            {
                "id": "archivo_cierre",
                "etiqueta": "Archivo de cierre mensual",
                "tipo": "archivo_excel",
                "requerido": True,
            },
            {
                "id": "carpeta_salida",
                "etiqueta": "Carpeta local de salida",
                "tipo": "carpeta",
                "requerido": True,
            },
        ]

    @property
    def archivo_generador(self) -> Path:
        return self.ruta_proyecto / "generar_informe_final.py"

    def validar_disponibilidad(self) -> Dict[str, Any]:
        faltantes = []
        for ruta in (
            self.archivo_generador,
            self.ruta_proyecto / "motor" / "proceso_completo.py",
        ):
            if not ruta.exists():
                faltantes.append(str(ruta))

        if faltantes:
            return {
                "disponible": False,
                "mensaje": "Faltan archivos del motor: " + ", ".join(faltantes),
            }

        return {
            "disponible": True,
            "mensaje": "Motor real de Comisiones disponible.",
        }

    def _buscar_configuracion(self) -> Optional[Path]:
        candidatos = [
            self.ruta_proyecto / "config" / "configuracion.yaml",
            self.ruta_proyecto / "configuracion" / "configuracion.yaml",
            self.ruta_proyecto / "configuracion.yaml",
        ]
        return next((ruta for ruta in candidatos if ruta.exists()), None)

    @staticmethod
    def _extraer_entero_yaml(texto: str, nombres: List[str]) -> Optional[int]:
        for nombre in nombres:
            patron = rf"(?im)^\s*{re.escape(nombre)}\s*:\s*[\"']?([0-9]{{1,4}})"
            coincidencia = re.search(patron, texto)
            if coincidencia:
                return int(coincidencia.group(1))
        return None

    def _periodo_configurado(self) -> Dict[str, Optional[int]]:
        ruta = self._buscar_configuracion()
        if ruta is None:
            return {"anio": None, "mes": None}

        texto = ruta.read_text(encoding="utf-8", errors="replace")
        return {
            "anio": self._extraer_entero_yaml(
                texto,
                ["anio", "año", "anio_proceso", "año_proceso"],
            ),
            "mes": self._extraer_entero_yaml(
                texto,
                ["mes", "mes_proceso", "numero_mes"],
            ),
        }

    def validar_parametros(self, parametros: Dict[str, Any]) -> List[str]:
        errores = []
        disponibilidad = self.validar_disponibilidad()
        if not disponibilidad["disponible"]:
            errores.append(disponibilidad["mensaje"])

        try:
            anio = int(parametros.get("anio", 0))
            if anio < 2000 or anio > 2100:
                errores.append("El año debe estar entre 2000 y 2100.")
        except (TypeError, ValueError):
            errores.append("El año debe ser numérico.")
            anio = None

        try:
            mes = int(parametros.get("mes", 0))
            if mes < 1 or mes > 12:
                errores.append("El mes debe estar entre 1 y 12.")
        except (TypeError, ValueError):
            errores.append("El mes debe ser numérico.")
            mes = None

        try:
            validar_salida_local(str(parametros.get("carpeta_salida", "")))
        except Exception as error:
            errores.append(str(error))

        texto_cierre = str(parametros.get("archivo_cierre", "")).strip()
        ruta_cierre = Path(texto_cierre) if texto_cierre else None
        if ruta_cierre is None:
            errores.append("Debe seleccionar el archivo de cierre mensual.")
        elif not ruta_cierre.exists() or not ruta_cierre.is_file():
            errores.append("No existe el archivo de cierre mensual seleccionado.")
        elif ruta_cierre.suffix.lower() not in {".xlsx", ".xlsm", ".xlsb"}:
            errores.append("El cierre mensual debe ser XLSX, XLSM o XLSB.")

        return errores

    def _python_del_proyecto(self) -> str:
        candidatos = [
            self.ruta_proyecto / ".venv" / "Scripts" / "python.exe",
            self.ruta_proyecto / "venv" / "Scripts" / "python.exe",
        ]
        for candidato in candidatos:
            if candidato.exists():
                return str(candidato)
        return sys.executable

    def _comando(self, anio: int, mes: int, ruta_cierre: Path) -> List[str]:
        codigo = (
            "import generar_informe_final as g; "
            "g.ejecutar("
            f"anio_proceso={anio!r}, "
            f"mes_proceso={mes!r}, "
            f"ruta_cierre={str(ruta_cierre)!r}"
            ")"
        )
        return [self._python_del_proyecto(), "-u", "-c", codigo]

    def _porcentaje_linea(self, linea: str, actual: int) -> int:
        texto = linea.strip().upper()
        encontrados = [valor for clave, valor in self.ETAPAS.items() if clave in texto]
        return max([actual] + encontrados)

    @staticmethod
    def _extraer_rutas_excel(texto: str) -> List[Path]:
        patron = r"(?i)([A-Z]:\\[^\r\n]*?\.xlsx)"
        rutas = []
        for valor in re.findall(patron, texto):
            ruta = Path(valor.strip().strip('"').strip("'"))
            if ruta.exists() and ruta not in rutas:
                rutas.append(ruta)
        return rutas

    def _ultimo_informe_generado(self, inicio_ns: int, salida_consola: str) -> Optional[Path]:
        rutas = self._extraer_rutas_excel(salida_consola)
        if rutas:
            return max(rutas, key=lambda ruta: ruta.stat().st_mtime_ns)

        candidatos = []
        for carpeta in (
            self.ruta_proyecto / "salida",
            self.ruta_proyecto,
        ):
            if carpeta.exists():
                for ruta in carpeta.glob("Informe_Comisiones_*.xlsx"):
                    try:
                        if ruta.stat().st_mtime_ns >= inicio_ns:
                            candidatos.append(ruta)
                    except OSError:
                        continue
        return max(candidatos, key=lambda ruta: ruta.stat().st_mtime_ns) if candidatos else None

    @staticmethod
    def _copiar_resultado(origen: Path, carpeta_salida: Path) -> Path:
        destino = carpeta_salida / origen.name
        if origen.resolve() == destino.resolve():
            return origen.resolve()
        if destino.exists():
            base = destino.stem
            sufijo = destino.suffix
            contador = 2
            while destino.exists():
                destino = carpeta_salida / f"{base}_{contador}{sufijo}"
                contador += 1
        shutil.copy2(origen, destino)
        return destino.resolve()

    def ejecutar(
        self,
        parametros: Dict[str, Any],
        reportar_evento: ReportadorEvento,
    ) -> Dict[str, Any]:
        self._cancelacion_solicitada = False
        anio = int(parametros["anio"])
        mes = int(parametros["mes"])
        carpeta_salida = validar_salida_local(parametros["carpeta_salida"])
        ruta_cierre = Path(parametros["archivo_cierre"]).expanduser().resolve()
        inicio_ns = __import__("time").time_ns()
        salida = []
        porcentaje = 2

        reportar_evento(
            "INICIANDO",
            f"Comisiones para {anio}-{mes:02d}. El resultado es informativo.",
            porcentaje,
        )

        entorno = os.environ.copy()
        entorno["PYTHONIOENCODING"] = "utf-8"
        entorno["PYTHONUNBUFFERED"] = "1"

        try:
            self._proceso = subprocess.Popen(
                self._comando(anio, mes, ruta_cierre),
                cwd=str(self.ruta_proyecto),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=entorno,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW
                    if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW")
                    else 0
                ),
            )

            assert self._proceso.stdout is not None
            for linea in self._proceso.stdout:
                limpia = linea.rstrip()
                salida.append(limpia)
                porcentaje = self._porcentaje_linea(limpia, porcentaje)
                if limpia:
                    reportar_evento("COMISIONES", limpia, porcentaje)
                if self._cancelacion_solicitada:
                    break

            codigo = self._proceso.wait()
        except Exception as error:
            return ResultadoEjecucion(
                exitoso=False,
                estado="ERROR",
                mensaje="No fue posible iniciar el motor de Comisiones.",
                errores=[str(error)],
            ).como_diccionario()
        finally:
            self._proceso = None

        if self._cancelacion_solicitada:
            return ResultadoEjecucion(
                exitoso=False,
                estado="CANCELADO",
                mensaje="La ejecución fue cancelada.",
            ).como_diccionario()

        texto_salida = "\n".join(salida)
        if codigo != 0:
            return ResultadoEjecucion(
                exitoso=False,
                estado="ERROR",
                mensaje=f"El motor de Comisiones terminó con código {codigo}.",
                errores=[texto_salida[-6000:]],
            ).como_diccionario()

        informe = self._ultimo_informe_generado(inicio_ns, texto_salida)
        if informe is None:
            return ResultadoEjecucion(
                exitoso=False,
                estado="ERROR",
                mensaje="El motor finalizó, pero no se encontró el informe generado.",
                errores=[
                    "Revise que generar_informe_final.py imprima o guarde el informe "
                    "en la carpeta local de salida del proyecto."
                ],
            ).como_diccionario()

        try:
            informe_local = self._copiar_resultado(informe, carpeta_salida)
        except Exception as error:
            return ResultadoEjecucion(
                exitoso=False,
                estado="ERROR",
                mensaje="El informe se generó, pero no pudo copiarse a la carpeta seleccionada.",
                archivos_generados=[str(informe.resolve())],
                errores=[str(error)],
            ).como_diccionario()

        estado_motor = "REVISAR" if re.search(r"Estado general:\s*REVISAR", texto_salida, re.I) else "OK"

        def extraer_entero_salida(etiquetas):
            for etiqueta in etiquetas:
                coincidencia = re.search(
                    rf"(?im)^\s*{re.escape(etiqueta)}\s*:\s*([0-9][0-9.,]*)",
                    texto_salida,
                )
                if coincidencia:
                    texto = coincidencia.group(1).replace(".", "").replace(",", "")
                    try:
                        return int(texto)
                    except ValueError:
                        return None
            return None

        metricas = {
            "anio": anio,
            "mes": mes,
            "periodo": f"{anio}-{mes:02d}",
            "archivo_cierre": str(ruta_cierre),
            "estado_motor": estado_motor,
            "registros_contables": extraer_entero_salida([
                "Filas Qry_Cta250115", "Registros contables"
            ]),
            "facturas_pendientes": extraer_entero_salida([
                "Facturas pendientes", "Facturas procesadas"
            ]),
            "llaves": extraer_entero_salida([
                "Llaves conciliadas", "Llaves procesadas"
            ]),
            "negocios": extraer_entero_salida([
                "Negocios consolidados", "Negocios procesados"
            ]),
            "informe_origen": str(informe.resolve()),
        }

        advertencias = []
        estado = "FINALIZADO"
        if estado_motor == "REVISAR":
            estado = "FINALIZADO CON ADVERTENCIAS"
            advertencias.append(
                "El informe contiene diferencias o controles informativos para revisar. "
                "Esto no representa una falla del aplicativo."
            )

        reportar_evento("FINALIZADO", f"Informe disponible en {informe_local}", 100)
        return ResultadoEjecucion(
            exitoso=True,
            estado=estado,
            mensaje="Informe de Comisiones generado correctamente.",
            archivos_generados=[str(informe_local)],
            carpeta_salida=str(carpeta_salida),
            advertencias=advertencias,
            metricas=metricas,
        ).como_diccionario()

    def cancelar(self) -> None:
        self._cancelacion_solicitada = True
        if self._proceso is not None and self._proceso.poll() is None:
            try:
                self._proceso.terminate()
            except OSError:
                pass
