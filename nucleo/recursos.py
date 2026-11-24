# -*- coding: utf-8 -*-
"""Módulo de resolución de rutas y recursos para ejecución en desarrollo y compilada (.exe)."""

import os
import sys
from pathlib import Path


def esta_congelado() -> bool:
    """Indica si la aplicación se está ejecutando como ejecutable compilado (PyInstaller)."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def obtener_directorio_aplicacion() -> Path:
    """
    Retorna la ruta raíz donde reside la aplicación.
    - En modo compilado (.exe): La carpeta donde está el ejecutable.
    - En modo desarrollo: La carpeta raíz del repositorio Plataforma_Procesos.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def obtener_ruta_recurso(ruta_relativa: str) -> Path:
    """
    Obtiene la ruta a un recurso interno (iconos, temas, configuraciones base).
    En modo congelado, busca en sys._MEIPASS si existe allí.
    """
    if esta_congelado():
        base_recurso = Path(sys._MEIPASS)
        candidato = base_recurso / ruta_relativa
        if candidato.exists():
            return candidato

    return obtener_directorio_aplicacion() / ruta_relativa


def asegurar_directorio_datos() -> Path:
    """
    Asegura un directorio seguro para almacenamiento de datos corporativos (historial, logs, prefs).
    En entornos restringidos sin permisos de escritura en la carpeta del .exe,
    utiliza %LOCALAPPDATA%/Bancolombia_Plataforma_Procesos.
    """
    dir_local = obtener_directorio_aplicacion()
    prueba_escritura = dir_local / ".test_write"
    try:
        prueba_escritura.touch()
        prueba_escritura.unlink()
        return dir_local
    except OSError:
        appdata = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Bancolombia_Plataforma_Procesos"
        appdata.mkdir(parents=True, exist_ok=True)
        return appdata
