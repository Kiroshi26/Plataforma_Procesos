import customtkinter as ctk
from interfaz.estilos import FUENTE, COLORES

class PaginaProcesos(ctk.CTkScrollableFrame):
    def __init__(self, parent, registro, on_abrir_proceso):
        super().__init__(parent, fg_color="transparent")
        self.registro = registro
        self.on_abrir_proceso = on_abrir_proceso

        ctk.CTkLabel(self, text="Procesos", text_color=COLORES["texto"],
                     font=(FUENTE, 28, "bold")).pack(anchor="w", padx=25, pady=(26, 4))
        ctk.CTkLabel(self, text="Selecciona un módulo para configurar y ejecutar.",
                     text_color=COLORES["texto_secundario"], font=(FUENTE, 14)).pack(anchor="w", padx=25)

        rejilla = ctk.CTkFrame(self, fg_color="transparent")
        rejilla.pack(fill="both", expand=True, padx=20, pady=18)
        
        for columna in range(2):
            rejilla.grid_columnconfigure(columna, weight=1, uniform="procesos")

        for indice, meta in enumerate(registro.listar()):
            proyecto = registro.obtener(meta["id"])
            try:
                disponibilidad = proyecto.validar_disponibilidad()
            except Exception as error:
                disponibilidad = {"disponible": False, "mensaje": str(error)}
            card = self._crear_tarjeta(rejilla, meta, disponibilidad)
            card.grid(row=indice//2, column=indice%2, sticky="nsew", padx=10, pady=10)

    def _crear_tarjeta(self, parent, meta, disponibilidad):
        card = ctk.CTkFrame(parent, fg_color=COLORES["panel"], corner_radius=8,
                            border_width=1, border_color=COLORES["borde"])
        
        color = COLORES["verde"] if disponibilidad.get("disponible") else COLORES["rojo"]
        
        borde_izq = ctk.CTkFrame(card, fg_color=color, width=6, corner_radius=0)
        borde_izq.pack(side="left", fill="y")
        
        contenido = ctk.CTkFrame(card, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=16, pady=16)
        
        ctk.CTkLabel(contenido, text=meta.get("nombre", meta["id"]), text_color=COLORES["texto"],
                     font=(FUENTE, 16, "bold")).pack(anchor="w")
        ctk.CTkLabel(contenido, text=meta.get("descripcion", ""), wraplength=450, justify="left",
                     text_color=COLORES["texto_secundario"], font=(FUENTE, 13)).pack(anchor="w", pady=(8, 12))
        ctk.CTkLabel(contenido, text=disponibilidad.get("mensaje", ""), wraplength=450, justify="left",
                     text_color=color, font=(FUENTE, 12, "bold")).pack(anchor="w")
                     
        ctk.CTkButton(contenido, text="Abrir módulo →", fg_color=COLORES["primario"], text_color="white",
                      hover_color=COLORES["primario_hover"], font=(FUENTE, 13, "bold"),
                      corner_radius=6, command=lambda: self.on_abrir_proceso(meta["id"])).pack(anchor="e", pady=(15, 0))
        return card
