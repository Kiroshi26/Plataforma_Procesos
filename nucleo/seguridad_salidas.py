from pathlib import Path


class ErrorSeguridadSalida(RuntimeError):
    pass


def validar_salida_local(ruta: str) -> Path:
    if not str(ruta).strip():
        raise ErrorSeguridadSalida("Debe indicar una carpeta local de salida.")

    carpeta = Path(ruta).expanduser()
    texto = str(carpeta).lower()

    if texto.startswith("\\\\") or texto.startswith("//"):
        raise ErrorSeguridadSalida(
            "La salida de prueba no puede ser una ubicación de red."
        )

    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta.resolve()


def bloquear_publicacion_corporativa(autorizada: bool) -> None:
    if autorizada:
        raise ErrorSeguridadSalida(
            "La publicación corporativa de Inversiones permanece bloqueada "
            "hasta aprobación explícita."
        )
