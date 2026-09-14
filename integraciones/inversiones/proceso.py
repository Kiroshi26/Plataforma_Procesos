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
    cantidad_baseneg: int
    total_mes: float


def ejecutar(
    configuracion: dict,
    anio: int,
    mes: int,
    usuario: str,
    clave: str,
    ruta_proyecto: str,
) -> ResultadoModuloInversiones:

    raiz_inversiones = Path(
        ruta_proyecto
    ).resolve()

    carpeta_src = (
        raiz_inversiones /
        "src"
    )

    if not raiz_inversiones.exists():
        raise ErrorModuloInversiones(
            f"No existe el proyecto de Inversiones: "
            f"{raiz_inversiones}"
        )

    if not carpeta_src.exists():
        raise ErrorModuloInversiones(
            f"No existe la carpeta src: "
            f"{carpeta_src}"
        )

    # Para que Python pueda resolver imports como:
    # from src.insumos import ...
    ruta_raiz = str(
        raiz_inversiones
    )

    if ruta_raiz not in sys.path:
        sys.path.insert(
            0,
            ruta_raiz
        )

    try:
        from src.insumos import (
            cargar_insumos,
        )

        from src.parametros import (
            crear_parametros,
        )

        from src.procesamiento import (
            preparar_insumos,
        )

        from src.proceso_inversiones import (
            ejecutar_proceso_inversiones,
        )

    except ImportError as error:
        raise ErrorModuloInversiones(
            "No fue posible importar el motor original "
            f"de Inversiones desde {raiz_inversiones}. "
            f"Detalle: {error}"
        ) from error

    parametros = crear_parametros(
        anio=anio,
        mes=mes,
    )

    insumos = cargar_insumos(
        configuracion
    )

    resultado_preparacion = preparar_insumos(
        insumos
    )

    resultado = ejecutar_proceso_inversiones(
        configuracion=configuracion,
        parametros=parametros,
        resultado_preparacion=resultado_preparacion,
        usuario=usuario,
        clave=clave,
    )

    return ResultadoModuloInversiones(
        exitoso=True,
        periodo=parametros.periodo,
        archivo_saldos=resultado.ruta_archivo,
        cantidad_saldos=resultado.cantidad_saldos,
        cantidad_baseneg=resultado.cantidad_baseneg,
        total_mes=resultado.total_mes,
    )