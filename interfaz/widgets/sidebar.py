import tkinter as tk
from interfaz.estilos import COLORES, FUENTE


class Sidebar(tk.Frame):
    ANCHO_EXPANDIDO = 210
    ANCHO_COLAPSADO = 68

    def __init__(self, parent, on_navegar=None):
        super().__init__(parent, bg=COLORES["panel"], width=self.ANCHO_EXPANDIDO,
                         highlightbackground=COLORES["borde"], highlightthickness=1)
        self.pack_propagate(False)
        self.on_navegar = on_navegar
        self.colapsada = False
        self.seleccion = "inicio"
        self.botones = {}

        cabecera = tk.Frame(self, bg=COLORES["panel"])
        cabecera.pack(fill="x", padx=10, pady=(12, 18))
        tk.Label(cabecera, text="AP", bg=COLORES["primario"], fg="white",
                 font=(FUENTE, 11, "bold"), width=3, height=2).pack(side="left")
        self.btn_colapsar = tk.Button(cabecera, text="‹", command=self.alternar, relief="flat", bd=0,
                                      bg=COLORES["panel"], fg=COLORES["texto_secundario"],
                                      font=(FUENTE, 16), cursor="hand2")
        self.btn_colapsar.pack(side="right")
        self.opciones = [
            ("inicio", "⌂", "Inicio"),
            ("procesos", "▦", "Procesos"),
            ("monitoreo", "◉", "Monitoreo"),
            ("configuracion", "⚙", "Configuración"),
        ]
        for clave, icono, texto in self.opciones:
            boton = tk.Button(self, text=f"{icono}   {texto}", anchor="w", relief="flat", bd=0,
                              bg=COLORES["panel"], fg=COLORES["texto"],
                              activebackground=COLORES["primario_suave"], activeforeground=COLORES["primario"],
                              font=(FUENTE, 10), padx=16, pady=11, cursor="hand2",
                              command=lambda c=clave: self.seleccionar(c, notificar=True))
            boton.pack(fill="x", padx=9, pady=2)
            self.botones[clave] = boton
        tk.Frame(self, bg=COLORES["panel"]).pack(fill="both", expand=True)
        self.seleccionar("inicio", notificar=False)

    def seleccionar(self, clave, notificar=False):
        self.seleccion = clave
        for nombre, boton in self.botones.items():
            activo = nombre == clave
            boton.configure(bg=COLORES["primario_suave"] if activo else COLORES["panel"],
                            fg=COLORES["primario"] if activo else COLORES["texto"],
                            font=(FUENTE, 10, "bold" if activo else "normal"))
        if notificar and self.on_navegar:
            self.on_navegar(clave)

    def alternar(self):
        self.colapsada = not self.colapsada
        self.configure(width=self.ANCHO_COLAPSADO if self.colapsada else self.ANCHO_EXPANDIDO)
        self.btn_colapsar.configure(text="›" if self.colapsada else "‹")
        for clave, icono, texto in self.opciones:
            self.botones[clave].configure(text=icono if self.colapsada else f"{icono}   {texto}",
                                          anchor="center" if self.colapsada else "w",
                                          padx=8 if self.colapsada else 16)
