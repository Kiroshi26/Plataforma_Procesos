import tkinter as tk

from interfaz.estilos import COLORES, FUENTE


class DashboardPage(tk.Frame):
    def __init__(self, parent, registro, on_abrir_proceso=None):
        super().__init__(parent, bg=COLORES["fondo"])
        self.registro = registro
        self.on_abrir_proceso = on_abrir_proceso
        procesos = registro.listar()
        disponibles = 0
        for meta in procesos:
            try:
                if registro.obtener(meta["id"]).validar_disponibilidad().get("disponible"):
                    disponibles += 1
            except Exception:
                pass

        cabecera = tk.Frame(self, bg=COLORES["fondo"])
        cabecera.pack(fill="x", padx=28, pady=(26, 18))
        tk.Label(cabecera, text="Inicio", bg=COLORES["fondo"], fg=COLORES["texto"],
                 font=(FUENTE, 22, "bold")).pack(anchor="w")
        tk.Label(cabecera, text="Resumen general de la plataforma", bg=COLORES["fondo"],
                 fg=COLORES["texto_secundario"], font=(FUENTE, 10)).pack(anchor="w", pady=(4, 0))

        metricas = tk.Frame(self, bg=COLORES["fondo"])
        metricas.pack(fill="x", padx=23)
        datos = [("Procesos", len(procesos), COLORES["primario"]),
                 ("Disponibles", disponibles, COLORES["verde"]),
                 ("No disponibles", len(procesos)-disponibles, COLORES["rojo"])]
        for titulo, valor, color in datos:
            self._metrica(metricas, titulo, valor, color).pack(side="left", fill="x", expand=True, padx=5)

        tk.Label(self, text="Procesos disponibles", bg=COLORES["fondo"], fg=COLORES["texto"],
                 font=(FUENTE, 13, "bold")).pack(anchor="w", padx=28, pady=(25, 10))
        contenedor = tk.Frame(self, bg=COLORES["fondo"])
        contenedor.pack(fill="x", padx=23)
        for meta in procesos:
            self._proceso(contenedor, meta).pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def _metrica(self, parent, titulo, valor, color):
        card = tk.Frame(parent, bg=COLORES["panel"], highlightbackground=COLORES["borde"], highlightthickness=1)
        tk.Frame(card, bg=color, height=3).pack(fill="x")
        tk.Label(card, text=titulo, bg=COLORES["panel"], fg=COLORES["texto_secundario"],
                 font=(FUENTE, 9)).pack(anchor="w", padx=16, pady=(14, 3))
        tk.Label(card, text=str(valor), bg=COLORES["panel"], fg=COLORES["texto"],
                 font=(FUENTE, 22, "bold")).pack(anchor="w", padx=16, pady=(0, 14))
        return card

    def _proceso(self, parent, meta):
        card = tk.Frame(parent, bg=COLORES["panel"], highlightbackground=COLORES["borde"], highlightthickness=1)
        tk.Label(card, text=meta.get("nombre", meta.get("id", "Proceso")), bg=COLORES["panel"],
                 fg=COLORES["texto"], font=(FUENTE, 11, "bold")).pack(anchor="w", padx=16, pady=(15, 5))
        tk.Label(card, text=meta.get("estado", "Disponible"), bg=COLORES["panel"], fg=COLORES["verde"],
                 font=(FUENTE, 9, "bold")).pack(anchor="w", padx=16)
        tk.Button(card, text="Abrir  →", relief="flat", bd=0, bg=COLORES["panel"], fg=COLORES["primario"],
                  activebackground=COLORES["primario_suave"], font=(FUENTE, 9, "bold"), cursor="hand2",
                  command=lambda: self.on_abrir_proceso and self.on_abrir_proceso(meta["id"])).pack(anchor="e", padx=12, pady=14)
        return card
