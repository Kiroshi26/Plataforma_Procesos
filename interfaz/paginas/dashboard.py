import tkinter as tk


class DashboardPage(tk.Frame):

    def __init__(self, parent, registro):

        super().__init__(
            parent,
            bg="#FFFFFF"
        )

        total_procesos = len(
            registro.listar()
        )

        titulo = tk.Label(
            self,
            text="Dashboard",
            bg="#FFFFFF",
            fg="#17365D",
            font=("Segoe UI", 22, "bold")
        )

        titulo.pack(
            anchor="w",
            padx=30,
            pady=(30, 10)
        )

        subtitulo = tk.Label(
            self,
            text="Resumen general de la plataforma.",
            bg="#FFFFFF",
            fg="#64748B",
            font=("Segoe UI", 10)
        )

        subtitulo.pack(
            anchor="w",
            padx=30
        )

        fila = tk.Frame(
            self,
            bg="#FFFFFF"
        )

        fila.pack(
            fill="x",
            padx=30,
            pady=25
        )

        self._tarjeta(
            fila,
            "Procesos",
            total_procesos
        ).pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        self._tarjeta(
            fila,
            "Ejecuciones",
            "0"
        ).pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        self._tarjeta(
            fila,
            "Resultados",
            "0"
        ).pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        self._tarjeta(
            fila,
            "Errores",
            "0"
        ).pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        actividad = tk.LabelFrame(
            self,
            text="Actividad reciente",
            bg="#FFFFFF",
            fg="#17365D",
            font=("Segoe UI", 10, "bold")
        )

        actividad.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 20)
        )

        tk.Label(
            actividad,
            text="Aún no existen ejecuciones registradas.",
            bg="#FFFFFF",
            fg="#64748B",
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            padx=15,
            pady=15
        )

    def _tarjeta(
        self,
        parent,
        titulo,
        valor
    ):

        tarjeta = tk.Frame(
            parent,
            bg="#F8FAFC",
            highlightbackground="#DCE3EC",
            highlightthickness=1
        )

        tk.Label(
            tarjeta,
            text=titulo,
            bg="#F8FAFC",
            fg="#64748B",
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 5)
        )

        tk.Label(
            tarjeta,
            text=str(valor),
            bg="#F8FAFC",
            fg="#1E293B",
            font=("Segoe UI", 24, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 15)
        )

        return tarjeta