from typing import Dict

from nucleo.contrato_proyecto import ContratoProyecto


class RegistroProyectos:
    def __init__(self) -> None:
        self._proyectos: Dict[str, ContratoProyecto] = {}

    def registrar(self, proyecto: ContratoProyecto) -> None:
        metadatos = proyecto.obtener_metadatos()
        identificador = str(metadatos["id"]).strip().lower()
        if identificador in self._proyectos:
            raise ValueError(f"El proyecto '{identificador}' ya está registrado.")
        self._proyectos[identificador] = proyecto

    def obtener(self, identificador: str) -> ContratoProyecto:
        clave = identificador.strip().lower()
        if clave not in self._proyectos:
            raise KeyError(f"Proyecto no registrado: {identificador}")
        return self._proyectos[clave]

    def listar(self):
        return [
            proyecto.obtener_metadatos()
            for proyecto in self._proyectos.values()
        ]
