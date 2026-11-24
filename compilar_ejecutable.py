# -*- coding: utf-8 -*-
"""
Script de compilación automatizado para generar el Ejecutable Corporativo (.EXE)
de Plataforma de Procesos Bancolombia.

Uso:
    python compilar_ejecutable.py [--un-solo-archivo]

Requisitos:
    pip install -r requirements.txt
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

RUTA_BASE = Path(__file__).resolve().parent


def encontrar_paquete_customtkinter():
    try:
        import customtkinter
        return Path(customtkinter.__file__).parent
    except ImportError:
        print("[ADVERTENCIA] customtkinter no está instalado en este entorno de Python.")
        return None


def crear_leeme_distribucion(carpeta_dist):
    contenido = """================================================================================
BANCOLOMBIA - APLICATIVO DE PROCESOS (DISTRIBUCIÓN CORPORATIVA PORTABLE)
================================================================================

Este aplicativo es PORTABLE y NO REQUIERE PERMISOS DE ADMINISTRADOR.

Instrucciones de uso:
1. Puede copiar o mover esta carpeta a cualquier ubicación de su computador
   (ej. C:\\Proyectos, su Escritorio o Documentos).
2. Para iniciar la aplicación, haga doble clic en:
   PlataformaProcesos.exe

Módulos incluidos:
- Comisiones 250115 (Conciliación mensual y facturación)
- Inversiones Fiduciarias (Conciliación contable vs Formato 351 y Óptima)
- Cruce de Efectivo (Extracción y lectura masiva de extractos PDF)

Configuración:
Las rutas a los proyectos o repositorios pueden modificarse en:
configuracion\\plataforma.json

Seguridad:
- Mantenga sus credenciales protegidas.
- No distribuya este paquete fuera de la red autorizada.
================================================================================
"""
    ruta_leeme = carpeta_dist / "LEEME_CORPORATIVO.txt"
    ruta_leeme.write_text(contenido, encoding="utf-8")


def compilar(un_solo_archivo=False):
    print("=" * 76)
    print(" COMPILADOR CORPORATIVO - BANCOLOMBIA PLATAFORMA DE PROCESOS")
    print("=" * 76)

    # 1. Verificar PyInstaller
    try:
        import PyInstaller
        print(f"[OK] PyInstaller detectado: versión {PyInstaller.__version__}")
    except ImportError:
        print("[ERROR] PyInstaller no está instalado. Ejecute: pip install pyinstaller")
        return False

    # 2. Localizar CustomTkinter
    dir_ctk = encontrar_paquete_customtkinter()
    separador_datos = ";" if os.name == "nt" else ":"

    # 3. Construir argumentos de PyInstaller
    comando = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--windowed",  # Sin ventana negra de consola
        "--name",
        "PlataformaProcesos",
        "--clean",
    ]

    if un_solo_archivo:
        print("[INFO] Modo: Archivo único (--onefile)")
        comando.append("--onefile")
    else:
        print("[INFO] Modo: Carpeta distribuible portable (--onedir) - RECOMENDADO CORPORATIVO")
        comando.append("--onedir")

    # Incluir recursos y datos
    if dir_ctk and dir_ctk.exists():
        comando.extend(["--add-data", f"{dir_ctk}{separador_datos}customtkinter"])

    carpeta_config = RUTA_BASE / "configuracion"
    if carpeta_config.exists():
        comando.extend(["--add-data", f"{carpeta_config}{separador_datos}configuracion"])

    pdf_marca = RUTA_BASE / "BANCOLOMBIA MANUAL DE MARCA.pdf"
    if pdf_marca.exists():
        comando.extend(["--add-data", f"{pdf_marca}{separador_datos}."])

    # Motores externos si existen en el entorno
    ruta_comisiones = Path(r"C:\Proyectos\Proyecto_Comisiones\motor")
    if ruta_comisiones.exists():
        comando.extend(["--add-data", f"{ruta_comisiones}{separador_datos}motor"])

    ruta_inversiones = Path(r"C:\Proyectos\Proyecto_Inversiones\src")
    if ruta_inversiones.exists():
        comando.extend(["--add-data", f"{ruta_inversiones}{separador_datos}src"])

    ruta_cruce = Path(r"C:\Proyectos\Cruce_Efectivo-main\Cruce_Efectivo-main\procesos")
    if ruta_cruce.exists():
        comando.extend(["--add-data", f"{ruta_cruce}{separador_datos}procesos"])

    # Hidden imports críticos
    imports_ocultos = [
        "customtkinter",
        "pandas",
        "openpyxl",
        "pyyaml",
        "yaml",
        "pdfplumber",
        "pdfminer",
        "pdfminer.six",
        "pypdfium2",
        "pyodbc",
        "xlsxwriter",
        "pyxlsb",
        "PIL",
        "PIL.ImageTk",
    ]
    for imp in imports_ocultos:
        comando.extend(["--hidden-import", imp])

    # Archivo de entrada
    archivo_app = RUTA_BASE / "app.py"
    comando.append(str(archivo_app))

    print("\n[INFO] Ejecutando compilación...")
    print(" ".join(comando))
    print()

    resultado = subprocess.run(comando, cwd=str(RUTA_BASE))
    if resultado.returncode != 0:
        print("[ERROR] La compilación falló. Revise los mensajes anteriores.")
        return False

    # 4. Post-procesamiento
    carpeta_dist = RUTA_BASE / "dist" / "PlataformaProcesos"
    if carpeta_dist.exists():
        crear_leeme_distribucion(carpeta_dist)
        # Asegurar carpeta configuracion accesible
        dist_config = carpeta_dist / "configuracion"
        dist_config.mkdir(parents=True, exist_ok=True)
        if (carpeta_config / "plataforma.json").exists():
            shutil.copy2(carpeta_config / "plataforma.json", dist_config / "plataforma.json")

    print("\n" + "=" * 76)
    print(" ¡COMPILACIÓN CORPORATIVA FINALIZADA CON ÉXITO!")
    print(f" Ubicación: {carpeta_dist if not un_solo_archivo else RUTA_BASE / 'dist'}")
    print("=" * 76)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compilador corporativo de Plataforma de Procesos")
    parser.add_argument(
        "--un-solo-archivo",
        action="store_true",
        help="Genera un único archivo .exe en lugar de una carpeta portable.",
    )
    args = parser.parse_args()
    compilar(un_solo_archivo=args.un_solo_archivo)
