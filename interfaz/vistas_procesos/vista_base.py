# -*- coding: utf-8 -*-
import os
import subprocess
import sys
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Callable, Optional

import customtkinter as ctk
from interfaz.estilos import COLORES, FUENTE


class TarjetaSeccion(ctk.CTkFrame):
    """Contenedor estilo Card corporativa Bancolombia."""

    def __init__(self, parent, titulo: str, subtitulo: str = "", icono: str = "", **kwargs):
        super().__init__(
            parent,
            fg_color=COLORES["panel"],
            corner_radius=12,
            border_width=1,
            border_color=COLORES["borde"],
            **kwargs,
        )
        self.pack(fill="x", padx=28, pady=8)

        if titulo or icono:
            cabecera = ctk.CTkFrame(self, fg_color="transparent")
            cabecera.pack(fill="x", padx=18, pady=(14, 6))

            if icono:
                ctk.CTkLabel(
                    cabecera,
                    text=icono,
                    font=(FUENTE, 16),
                    width=28,
                    height=28,
                    corner_radius=6,
                    fg_color=COLORES["fondo_modulo"],
                    text_color=COLORES["texto"],
                ).pack(side="left", padx=(0, 10))

            txt_box = ctk.CTkFrame(cabecera, fg_color="transparent")
            txt_box.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(
                txt_box,
                text=titulo,
                font=(FUENTE, 14, "bold"),
                text_color=COLORES["texto"],
            ).pack(anchor="w")

            if subtitulo:
                ctk.CTkLabel(
                    txt_box,
                    text=subtitulo,
                    font=(FUENTE, 11),
                    text_color=COLORES["texto_secundario"],
                ).pack(anchor="w")

        self.cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        self.cuerpo.pack(fill="both", expand=True, padx=18, pady=(6, 16))


class BadgePill(ctk.CTkLabel):
    """Píldora de estado con colores corporativos."""

    VARIANTES = {
        "verde": (COLORES["fondo_pill_verde"], COLORES["verde"]),
        "amarillo": (COLORES["fondo_pill_amarillo"], COLORES["amarillo_estado"]),
        "azul": (COLORES["fondo_pill_azul"], COLORES["azul_estado"]),
        "rojo": (COLORES["fondo_pill_rojo"], COLORES["rojo"]),
        "gris": (COLORES["fondo_icono_gris"], COLORES["texto_secundario"]),
    }

    def __init__(self, parent, texto: str, variante: str = "verde", **kwargs):
        bg, fg = self.VARIANTES.get(variante, self.VARIANTES["verde"])
        super().__init__(
            parent,
            text=texto,
            fg_color=bg,
            text_color=fg,
            font=(FUENTE, 10, "bold"),
            corner_radius=6,
            height=22,
            padx=10,
            **kwargs,
        )


def abrir_archivo_o_carpeta(ruta_str: str):
    """Abre un archivo o carpeta en el explorador del sistema operativo."""
    if not ruta_str:
        return
    ruta = Path(ruta_str)
    if not ruta.exists():
        messagebox.showwarning("Ruta no encontrada", f"No se encontró la ruta:\n{ruta_str}")
        return

    try:
        if os.name == "nt":
            os.startfile(str(ruta))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(ruta)])
        else:
            subprocess.Popen(["xdg-open", str(ruta)])
    except Exception as error:
        messagebox.showerror("Error al abrir", str(error))
