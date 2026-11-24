# -*- coding: utf-8 -*-
import sys
from dataclasses import dataclass
from pathlib import Path


class ErrorModuloInversiones(Exception):
    pass


@dataclass
class ResultadoModuloInversiones:
    exitoso: bool
    periodo: str
    archivo_saldos: Path
    cantidad_saldos: int
    cantidad_subcuentas: int
    cantidad_baseneg: int
    total_saldo_contable: float
    total_saldo_f351: float
    total_diferencias: float
    registros_con_diferencia: int


def ejecutar(
    anio,
    mes,
    usuario,
    clave,
    ruta_proyecto,
    reportar_evento=None,
    saldos_override=None,
):
    raiz = Path(ruta_proyecto).resolve()
    carpeta_src = raiz / "src"
    ruta_config = raiz / "config.yaml"

    if not raiz.is_dir():
        raise ErrorModuloInversiones(f"No existe el proyecto de Inversiones: {raiz}")
    if not carpeta_src.is_dir():
        raise ErrorModuloInversiones(f"No existe la carpeta src: {carpeta_src}")
    if not ruta_config.is_file():
        raise ErrorModuloInversiones(f"No existe el archivo de configuración: {ruta_config}")

    ruta_raiz = str(raiz)
    if ruta_raiz not in sys.path:
        sys.path.insert(0, ruta_raiz)

    try:
        from src.configuracion import cargar_configuracion, validar_carpetas
        from src.insumos import cargar_insumos
        from src.parametros import crear_parametros
        from src.proceso_inversiones import ejecutar_proceso_inversiones
    except ImportError as error:
        raise ErrorModuloInversiones(
            f"No fue posible importar el motor de Inversiones desde {raiz}. Detalle: {error}"
        ) from error

    def evento(estado, mensaje, porcentaje):
        if reportar_evento:
            reportar_evento(estado, mensaje, porcentaje)

    evento("CONFIGURACION", "Cargando configuración de Inversiones.", 10)
    configuracion = cargar_configuracion(str(ruta_config))
    validar_carpetas(configuracion)

    parametros = crear_parametros(anio=anio, mes=mes)

    evento("INSUMOS", "Leyendo insumos locales (BASE_NEGOCIOS y Formato 351).", 25)
    insumos = cargar_insumos(configuracion)

    evento("PROCESO", "Consultando base de datos Óptima y ejecutando conciliación.", 55)
    resultado = ejecutar_proceso_inversiones(
        configuracion=configuracion,
        parametros=parametros,
        insumos=insumos,
        usuario=usuario,
        clave=clave,
        saldos_nacional_override=saldos_override,
    )

    evento("FINALIZADO", "Conciliación de Inversiones completada exitosamente.", 100)
    return ResultadoModuloInversiones(
        exitoso=True,
        periodo=parametros.periodo,
        archivo_saldos=Path(resultado.ruta_archivo),
        cantidad_saldos=resultado.cantidad_saldos,
        cantidad_subcuentas=resultado.cantidad_subcuentas,
        cantidad_baseneg=resultado.cantidad_baseneg,
        total_saldo_contable=resultado.total_saldo_contable,
        total_saldo_f351=resultado.total_saldo_f351,
        total_diferencias=resultado.total_diferencias,
        registros_con_diferencia=resultado.registros_con_diferencia,
    )
