# -*- coding: utf-8 -*-
"""Adaptador para integrar el motor de Cruce de Efectivo a la plataforma central."""

import sys
from pathlib import Path
from typing import Any, Dict, List

from nucleo.contrato_proyecto import ContratoProyecto
from nucleo.resultados import ResultadoEjecucion

PERIODOS_DISPONIBLES = [
    "01_ENE", "02_FEB", "03_MAR", "04_ABR",
    "05_MAY", "06_JUN", "07_JUL", "08_AGO",
    "09_SEP", "10_OCT", "11_NOV", "12_DIC",
]


class AdaptadorCruceEfectivo(ContratoProyecto):
    """Conecta Plataforma_Procesos con el motor de Cruce de Efectivo."""

    def __init__(self, ruta_proyecto: str) -> None:
        self.ruta_base = Path(ruta_proyecto)

    @property
    def ruta_proyecto(self) -> Path:
        """Resuelve la ruta efectiva del proyecto, manejando anidaciones de repositorio."""
        if (self.ruta_base / "procesos").exists():
            return self.ruta_base
        subcarpeta = self.ruta_base / "Cruce_Efectivo-main"
        if (subcarpeta / "procesos").exists():
            return subcarpeta
        return self.ruta_base

    def obtener_metadatos(self) -> Dict[str, Any]:
        return {
            "id": "cruce_efectivo",
            "nombre": "Cruce de Efectivo",
            "descripcion": (
                "Búsqueda y extracción masiva de extractos PDF fiduciarios "
                "y cruce con el maestro de cuentas bancarias."
            ),
            "estado": "INTEGRADO",
        }

    def obtener_campos_configuracion(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "criterio",
                "etiqueta": "Criterio de Búsqueda",
                "tipo": "texto",
                "requerido": True,
                "ayuda": "Código o sufijo del negocio/extracto (ej. FID, FND, o código específico).",
            },
            {
                "id": "anio",
                "etiqueta": "Año",
                "tipo": "entero",
                "requerido": True,
            },
            {
                "id": "periodo",
                "etiqueta": "Periodo / Mes",
                "tipo": "opcion",
                "opciones": PERIODOS_DISPONIBLES,
                "requerido": True,
            },
            {
                "id": "archivo_ctasbanc",
                "etiqueta": "Archivo de Cuentas Bancarias",
                "tipo": "archivo_excel",
                "requerido": False,
                "ayuda": "Excel con columnas: CUENTA CONTABLE, DESCRIPCION, NOMBRE ENTIDAD, MONEDA.",
            },
            {
                "id": "carpeta_salida",
                "etiqueta": "Carpeta Local de Salida",
                "tipo": "carpeta",
                "requerido": False,
            },
            {
                "id": "modo_masivo",
                "etiqueta": "Procesamiento Masivo (todos los criterios)",
                "tipo": "booleano",
                "requerido": False,
            },
        ]

    def validar_disponibilidad(self) -> Dict[str, Any]:
        ruta = self.ruta_proyecto
        if not ruta.exists() or not ruta.is_dir():
            return {
                "disponible": False,
                "mensaje": f"No se encontró la carpeta del proyecto Cruce de Efectivo: {ruta}",
            }

        requeridos = [
            ruta / "procesos" / "proceso_principal.py",
            ruta / "procesos" / "extractor_pdf.py",
            ruta / "procesos" / "exportador_excel.py",
            ruta / "procesos" / "lector_carpetas.py",
        ]
        faltantes = [str(p) for p in requeridos if not p.exists()]
        if faltantes:
            return {
                "disponible": False,
                "mensaje": "Faltan componentes del motor: " + ", ".join(faltantes),
            }

        return {
            "disponible": True,
            "mensaje": "Motor de Cruce de Efectivo disponible.",
        }

    def validar_parametros(self, parametros: Dict[str, Any]) -> List[str]:
        errores = []
        modo_masivo = bool(parametros.get("modo_masivo", False))
        criterio = str(parametros.get("criterio", "")).strip()
        anio_texto = str(parametros.get("anio", "")).strip()
        periodo = str(parametros.get("periodo", "")).strip()
        archivo_ctasbanc = str(parametros.get("archivo_ctasbanc", "")).strip()

        if not modo_masivo and not criterio:
            errores.append("Debe ingresar un Criterio de búsqueda (o activar el Modo Masivo).")

        try:
            anio = int(anio_texto)
            if anio < 2000 or anio > 2100:
                errores.append("El año debe ser un valor válido entre 2000 y 2100.")
        except (ValueError, TypeError):
            errores.append("El año debe ser numérico (ej. 2026).")

        if not periodo:
            errores.append("Seleccione un Periodo / Mes.")

        if archivo_ctasbanc:
            ruta_ctas = Path(archivo_ctasbanc)
            if not ruta_ctas.exists() or not ruta_ctas.is_file():
                errores.append(f"El archivo de cuentas bancarias no existe: {archivo_ctasbanc}")

        return errores

    def ejecutar(self, parametros: Dict[str, Any], reportar_evento) -> Dict[str, Any]:
        ruta_str = str(self.ruta_proyecto.resolve())
        if ruta_str not in sys.path:
            sys.path.insert(0, ruta_str)

        criterio = str(parametros.get("criterio", "")).strip()
        anio = str(parametros.get("anio", "2026")).strip()
        periodo = str(parametros.get("periodo", "01_ENE")).strip()
        archivo_ctasbanc = str(parametros.get("archivo_ctasbanc", "")).strip() or None
        carpeta_salida = str(parametros.get("carpeta_salida", "")).strip() or None
        modo_masivo = bool(parametros.get("modo_masivo", False))

        try:
            reportar_evento("INICIO", "Inicializando motor de Cruce de Efectivo...", 5)

            if modo_masivo:
                from procesos.proceso_masivo import ejecutar_masivo

                reportar_evento("BUSQUEDA", f"Iniciando escaneo masivo para el periodo {periodo}...", 10)
                archivos = ejecutar_masivo(
                    anio=anio,
                    periodo=periodo,
                    archivo_ctasbanc=archivo_ctasbanc,
                    reportar_evento=reportar_evento,
                )
                archivos_generados = [str(a) for a in (archivos or [])]
                mensaje = f"Proceso masivo finalizado. Generados {len(archivos_generados)} archivos."
            else:
                from procesos.proceso_principal import ejecutar as ejecutar_cruce

                reportar_evento("PROCESO", f"Ejecutando cruce para criterio '{criterio}' en {periodo}...", 15)
                archivo = ejecutar_cruce(
                    criterio=criterio,
                    anio=anio,
                    periodo=periodo,
                    archivo_ctasbanc=archivo_ctasbanc,
                    reportar_evento=reportar_evento,
                    carpeta_salida=carpeta_salida,
                )
                archivos_generados = [str(archivo)] if archivo else []
                mensaje = f"Cruce de Efectivo generado exitosamente para '{criterio}'."

            carpeta_final = ""
            if archivos_generados:
                carpeta_final = str(Path(archivos_generados[0]).parent)
            elif carpeta_salida:
                carpeta_final = carpeta_salida

            return ResultadoEjecucion(
                exitoso=bool(archivos_generados),
                estado="FINALIZADO" if archivos_generados else "SIN_RESULTADOS",
                mensaje=mensaje,
                archivos_generados=archivos_generados,
                carpeta_salida=carpeta_final,
                metricas={
                    "criterio": "MASIVO" if modo_masivo else criterio,
                    "periodo": f"{anio} - {periodo}",
                    "total_archivos": len(archivos_generados),
                    "archivo_principal": Path(archivos_generados[0]).name if archivos_generados else "Ninguno",
                },
            ).como_diccionario()

        except Exception as error:
            reportar_evento("ERROR", str(error), 100)
            return ResultadoEjecucion(
                exitoso=False,
                estado="ERROR",
                mensaje=f"Error en Cruce de Efectivo: {error}",
                errores=[str(error)],
            ).como_diccionario()
