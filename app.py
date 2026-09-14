import argparse
import json
from pathlib import Path

from integraciones.comisiones.adaptador import AdaptadorComisiones
from integraciones.inversiones.adaptador import AdaptadorInversiones
from nucleo.registro_proyectos import RegistroProyectos

RUTA_BASE = Path(__file__).resolve().parent


def cargar_configuracion():
    ruta = RUTA_BASE / "configuracion" / "plataforma.json"
    return json.loads(ruta.read_text(encoding="utf-8"))


def crear_registro(configuracion=None):
    configuracion = configuracion or cargar_configuracion()
    rutas = configuracion["rutas_proyectos"]
    registro = RegistroProyectos()
    registro.registrar(AdaptadorComisiones(rutas["comisiones"]))
    registro.registrar(AdaptadorInversiones(rutas["inversiones"]))
    return registro


def ejecutar_consola(configuracion, registro):
    print("=" * 72)
    print(configuracion["nombre"])
    print(f"Versión {configuracion['version']}")
    print("=" * 72)
    for proyecto in registro.listar():
        modulo = registro.obtener(proyecto["id"])
        disponibilidad = modulo.validar_disponibilidad()
        print()
        print(f"- {proyecto['nombre']}")
        print(f"  Estado: {proyecto['estado']}")
        print(f"  Disponible: {disponibilidad['disponible']}")
        print(f"  Detalle: {disponibilidad['mensaje']}")
    print()
    print("No se ejecutó ningún motor ni se publicaron resultados.")


def main():
    parser = argparse.ArgumentParser(description="Plataforma modular de procesos")
    parser.add_argument(
        "--consola",
        action="store_true",
        help="Muestra el inventario sin abrir la interfaz gráfica.",
    )
    argumentos = parser.parse_args()
    configuracion = cargar_configuracion()
    registro = crear_registro(configuracion)

    if argumentos.consola:
        ejecutar_consola(configuracion, registro)
        return

    from interfaz.ventana_principal import VentanaPrincipal

    ventana = VentanaPrincipal(registro, configuracion)
    ventana.mainloop()


if __name__ == "__main__":
    main()
