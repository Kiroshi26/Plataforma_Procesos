import tkinter as tk


class PaginaConfiguracion(tk.Frame):

    def __init__(self, parent):

        super().__init__(
            parent,
            bg="#F4F7FB"
        )

        titulo = tk.Label(
            self,
            text="Configuración",
            bg="#F4F7FB",
            fg="#17365D",
            font=("Segoe UI", 18, "bold")
        )

        titulo.pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )