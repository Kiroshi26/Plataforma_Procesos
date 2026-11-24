import json
from pathlib import Path
from nucleo.recursos import asegurar_directorio_datos, obtener_directorio_aplicacion


class GestorPreferencias:
    PREDETERMINADAS = {
        "tema": "claro",
        "recordar_ventana": True,
        "recordar_sidebar": True,
        "sidebar_colapsada": False,
        "mostrar_consola": True,
        "confirmar_cierre": True,
        "abrir_resultado_automaticamente": False,
        "geometria": "1280x800",
        "estado_ventana": "normal",
        "historial": r"C:\Proyectos\pruebas\Historial_AP",
    }

    def __init__(self, ruta=None):
        if ruta is None:
            dir_base = asegurar_directorio_datos()
            ruta = dir_base / "configuracion" / "preferencias_usuario.json"
        self.ruta = Path(ruta)
        self.datos = dict(self.PREDETERMINADAS)
        self.cargar()

    def cargar(self):
        if not self.ruta.exists():
            return self.datos
        try:
            with self.ruta.open("r", encoding="utf-8") as archivo:
                guardadas = json.load(archivo)
            if isinstance(guardadas, dict):
                self.datos.update(guardadas)
        except (OSError, json.JSONDecodeError):
            pass
        return self.datos

    def obtener(self, clave, predeterminado=None):
        return self.datos.get(clave, predeterminado)

    def actualizar(self, cambios):
        self.datos.update(cambios)
        self.guardar()

    def guardar(self):
        try:
            self.ruta.parent.mkdir(parents=True, exist_ok=True)
            temporal = self.ruta.with_suffix(".tmp")
            with temporal.open("w", encoding="utf-8") as archivo:
                json.dump(self.datos, archivo, ensure_ascii=False, indent=2)
            temporal.replace(self.ruta)
        except OSError:
            pass
