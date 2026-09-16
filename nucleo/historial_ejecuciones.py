import getpass
import json
import os
import socket
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path


class HistorialEjecuciones:
    CAMPOS_SENSIBLES = {
        "clave", "password", "contrasena", "contraseña", "token",
        "secret", "secreto", "credencial", "credenciales"
    }

    def __init__(self, carpeta_base=r"C:\Proyectos\pruebas\Historial_AP"):
        self.carpeta_base = Path(carpeta_base)

    def iniciar(self, metadatos, parametros):
        ahora = datetime.now()
        identificador = f"{ahora:%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}"
        registro = {
            "id": identificador,
            "proceso_id": str(metadatos.get("id", "")),
            "proceso_nombre": str(metadatos.get("nombre", metadatos.get("id", "Proceso"))),
            "usuario": getpass.getuser(),
            "equipo": socket.gethostname(),
            "inicio": ahora.isoformat(timespec="seconds"),
            "fin": None,
            "duracion_segundos": None,
            "estado": "EJECUTANDO",
            "exitoso": None,
            "parametros": self._sanitizar_parametros(parametros),
            "mensaje": "Ejecución iniciada.",
            "advertencias": [],
            "errores": [],
            "archivos_generados": [],
            "metricas": {},
            "eventos": [],
        }
        self.guardar(registro)
        return registro

    def agregar_evento(self, registro, estado, mensaje, porcentaje):
        if not registro:
            return
        registro["estado"] = str(estado)
        registro["eventos"].append({
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "estado": str(estado),
            "mensaje": str(mensaje),
            "porcentaje": int(porcentaje or 0),
        })
        self.guardar(registro)

    def finalizar(self, registro, resultado):
        if not registro:
            return
        fin = datetime.now()
        try:
            inicio = datetime.fromisoformat(registro["inicio"])
            duracion = max(0, int((fin - inicio).total_seconds()))
        except Exception:
            duracion = None
        registro.update({
            "fin": fin.isoformat(timespec="seconds"),
            "duracion_segundos": duracion,
            "estado": str(resultado.get("estado", "FINALIZADO")),
            "exitoso": bool(resultado.get("exitoso", False)),
            "mensaje": str(resultado.get("mensaje", "")),
            "advertencias": list(resultado.get("advertencias", []) or []),
            "errores": list(resultado.get("errores", []) or []),
            "archivos_generados": [str(x) for x in (resultado.get("archivos_generados", []) or [])],
            "metricas": deepcopy(resultado.get("metricas", {}) or {}),
        })
        self.guardar(registro)

    def guardar(self, registro):
        inicio = datetime.fromisoformat(registro["inicio"])
        carpeta = self.carpeta_base / f"{inicio:%Y}" / f"{inicio:%m}"
        carpeta.mkdir(parents=True, exist_ok=True)
        destino = carpeta / f"{registro['id']}.json"
        temporal = destino.with_suffix(".tmp")
        with temporal.open("w", encoding="utf-8") as archivo:
            json.dump(registro, archivo, ensure_ascii=False, indent=2, default=str)
        os.replace(temporal, destino)

    def listar(self, solo_usuario=None):
        if not self.carpeta_base.exists():
            return []
        registros = []
        for archivo in self.carpeta_base.rglob("*.json"):
            try:
                with archivo.open("r", encoding="utf-8") as entrada:
                    dato = json.load(entrada)
                if solo_usuario and dato.get("usuario") != solo_usuario:
                    continue
                registros.append(dato)
            except (OSError, json.JSONDecodeError):
                continue
        registros.sort(key=lambda x: x.get("inicio", ""), reverse=True)
        return registros

    def _sanitizar_parametros(self, parametros):
        limpios = {}
        for clave, valor in (parametros or {}).items():
            nombre = str(clave).lower().strip()
            if nombre in self.CAMPOS_SENSIBLES or any(s in nombre for s in self.CAMPOS_SENSIBLES):
                continue
            if isinstance(valor, (str, int, float, bool)) or valor is None:
                limpios[str(clave)] = valor
            else:
                limpios[str(clave)] = str(valor)
        return limpios
