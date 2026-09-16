import tkinter as tk

from interfaz.estilos import COLORES, FUENTE


class PaginaProcesos(tk.Frame):
    def __init__(self, parent, registro, on_abrir_proceso):
        super().__init__(parent, bg=COLORES["fondo"])
        self.registro = registro
        self.on_abrir_proceso = on_abrir_proceso

        tk.Label(self, text="Procesos", bg=COLORES["fondo"], fg=COLORES["texto"],
                 font=(FUENTE, 22, "bold")).pack(anchor="w", padx=28, pady=(26, 4))
        tk.Label(self, text="Selecciona un módulo para configurar y ejecutar.", bg=COLORES["fondo"],
                 fg=COLORES["texto_secundario"], font=(FUENTE, 10)).pack(anchor="w", padx=28)

        rejilla = tk.Frame(self, bg=COLORES["fondo"])
        rejilla.pack(fill="both", expand=True, padx=23, pady=18)
        for columna in range(2):
            rejilla.grid_columnconfigure(columna, weight=1, uniform="procesos")

        for indice, meta in enumerate(registro.listar()):
            proyecto = registro.obtener(meta["id"])
            try:
                disponibilidad = proyecto.validar_disponibilidad()
            except Exception as error:
                disponibilidad = {"disponible": False, "mensaje": str(error)}
            card = self._crear_tarjeta(rejilla, meta, disponibilidad)
            card.grid(row=indice//2, column=indice%2, sticky="nsew", padx=5, pady=5)

    def _crear_tarjeta(self, parent, meta, disponibilidad):
        card = tk.Frame(parent, bg=COLORES["panel"], highlightbackground=COLORES["borde"], highlightthickness=1)
        color = COLORES["verde"] if disponibilidad.get("disponible") else COLORES["rojo"]
        tk.Frame(card, bg=color, width=4).pack(side="left", fill="y")
        contenido = tk.Frame(card, bg=COLORES["panel"])
        contenido.pack(fill="both", expand=True, padx=16, pady=14)
        tk.Label(contenido, text=meta.get("nombre", meta["id"]), bg=COLORES["panel"], fg=COLORES["texto"],
                 font=(FUENTE, 12, "bold")).pack(anchor="w")
        tk.Label(contenido, text=meta.get("descripcion", ""), wraplength=380, justify="left",
                 bg=COLORES["panel"], fg=COLORES["texto_secundario"], font=(FUENTE, 9)).pack(anchor="w", pady=(5, 8))
        tk.Label(contenido, text=disponibilidad.get("mensaje", ""), wraplength=380, justify="left",
                 bg=COLORES["panel"], fg=color, font=(FUENTE, 9, "bold")).pack(anchor="w")
        tk.Button(contenido, text="Abrir módulo  →", relief="flat", bd=0, bg=COLORES["primario"], fg="white",
                  activebackground=COLORES["primario_hover"], activeforeground="white", font=(FUENTE, 9, "bold"),
                  padx=12, pady=7, cursor="hand2", command=lambda: self.on_abrir_proceso(meta["id"])).pack(anchor="e", pady=(12, 0))
        return card
