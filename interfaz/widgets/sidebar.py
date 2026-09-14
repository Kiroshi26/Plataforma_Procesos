import tkinter as tk


class Sidebar(tk.Frame):

    def __init__(self, parent):

        super().__init__(
            parent,
            bg="#FFFFFF",
            width=220,
            highlightbackground="#DCE3EC",
            highlightthickness=1
        )

        self.pack_propagate(False)

        self.botones = {}

        opciones = [

            ("inicio", "🏠 Inicio"),

            ("procesos", "📦 Procesos"),

            ("ejecuciones", "▶ Ejecuciones"),

            ("monitoreo", "📊 Monitoreo"),

            ("configuracion", "⚙ Configuración")

        ]

        for clave, texto in opciones:

            boton = tk.Button(
                self,
                text=texto,
                anchor="w",
                relief="flat",
                bg="#FFFFFF",
                font=("Segoe UI", 10, "bold"),
                padx=20,
                pady=12
            )

            boton.pack(
                fill="x",
                padx=10,
                pady=3
            )

            self.botones[clave] = boton