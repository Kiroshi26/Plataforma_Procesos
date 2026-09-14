import tkinter as tk

from interfaz.widgets.tarjeta_metrica import (
    TarjetaMetrica
)


class PaginaInicio(tk.Frame):

    def __init__(self, parent):

        super().__init__(
            parent,
            bg="#F4F7FB"
        )

        fila = tk.Frame(
            self,
            bg="#F4F7FB"
        )

        fila.pack(
            fill="x",
            pady=20,
            padx=20
        )

        tarjetas = [

            ("Procesos", 2),

            ("Ejecuciones", 0),

            ("Errores", 0),

            ("Resultados", 0),

        ]

        for titulo, valor in tarjetas:

            tarjeta = TarjetaMetrica(
                fila,
                titulo,
                valor
            )

            tarjeta.pack(
                side="left",
                fill="both",
                expand=True,
                padx=5
            )