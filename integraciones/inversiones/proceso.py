import sys
from copy import deepcopy
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
    cantidad_baseneg: int
    total_mes: float


def ejecutar(
    anio,
    mes,
    usuario,
    clave,
    ruta_proyecto,
    reportar_evento=None,
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
        from src.configuracion import (
            cargar_configuracion,
            validar_carpetas,
            validar_configuracion_red,
            validar_modo_seguro,
        )
        from src.insumos import cargar_insumos
        from src.insumos_red import preparar_insumos_desde_red
        from src.parametros import crear_parametros
        from src.procesamiento import preparar_insumos
        from src.proceso_inversiones import ejecutar_proceso_inversiones
    except ImportError as error:
        raise ErrorModuloInversiones(
            f"No fue posible importar el motor original desde {raiz}. Detalle: {error}"
        ) from error

    def evento(estado, mensaje, porcentaje):
        if reportar_evento:
            reportar_evento(estado, mensaje, porcentaje)

    evento("CONFIGURACION", "Cargando configuración original de Inversiones.", 10)
    configuracion = cargar_configuracion(str(ruta_config))
    validar_modo_seguro(configuracion)
    rutas_locales = validar_carpetas(configuracion)
    rutas_red = validar_configuracion_red(configuracion)

    parametros = crear_parametros(anio=anio, mes=mes)

    evento("INSUMOS", "Copiando insumos corporativos a una ejecución local.", 20)
    ejecucion = preparar_insumos_desde_red(
        configuracion=configuracion,
        rutas_red=rutas_red,
        carpeta_ejecuciones=rutas_locales["ejecuciones"],
        fecha_corte=parametros.fecha_corte,
    )

    # La configuración original no se modifica. Esta copia solo vive en memoria
    # durante la ejecución y hace que cargar_insumos lea los archivos congelados.
    configuracion_ejecucion = deepcopy(configuracion)
    configuracion_ejecucion["rutas"]["insumos_prueba"] = str(
        ejecucion.carpeta_ejecucion
    )
    configuracion_ejecucion["archivos"]["formato_351"] = ejecucion.formato_351.nombre
    configuracion_ejecucion["archivos"]["mapas_contables"] = ejecucion.mapas_contables.nombre
    configuracion_ejecucion["archivos"]["mapas_centros_costos"] = (
        ejecucion.mapas_centros_costos.nombre
    )

    evento("LECTURA", "Leyendo las copias locales de los insumos.", 40)
    insumos = cargar_insumos(configuracion_ejecucion)
    resultado_preparacion = preparar_insumos(insumos)

    evento("PROCESO", "Ejecutando consulta y conciliación de Inversiones.", 60)
    resultado = ejecutar_proceso_inversiones(
        configuracion=configuracion_ejecucion,
        parametros=parametros,
        resultado_preparacion=resultado_preparacion,
        usuario=usuario,
        clave=clave,
    )

    evento("FINALIZADO", "Proceso de Inversiones finalizado.", 100)
    return ResultadoModuloInversiones(
        exitoso=True,
        periodo=parametros.periodo,
        archivo_saldos=Path(resultado.ruta_archivo),
        cantidad_saldos=resultado.cantidad_saldos,
        cantidad_baseneg=resultado.cantidad_baseneg,
        total_mes=resultado.total_mes,
    )
