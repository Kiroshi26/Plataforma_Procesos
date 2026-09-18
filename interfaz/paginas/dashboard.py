import customtkinter as ctk
from interfaz.estilos import FUENTE, COLORES

class DashboardPage(ctk.CTkScrollableFrame):
    def __init__(self, parent, registro, on_abrir_proceso=None):
        super().__init__(parent, fg_color="transparent")
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
                
        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(cabecera, text="Inicio", text_color=COLORES["texto"], 
                     font=(FUENTE, 28, "bold")).pack(anchor="w")
        ctk.CTkLabel(cabecera, text="Resumen general de la plataforma", 
                     text_color=COLORES["texto_secundario"], font=(FUENTE, 14)).pack(anchor="w", pady=(0, 10))
                     
        metricas = ctk.CTkFrame(self, fg_color="transparent")
        metricas.pack(fill="x", padx=15)
        
        datos = [
            ("Procesos", len(procesos), COLORES["primario"]),
            ("Disponibles", disponibles, COLORES["verde"]),
            ("No disponibles", len(procesos) - disponibles, COLORES["rojo"])
        ]
        
        for i, (titulo, valor, color) in enumerate(datos):
            metricas.grid_columnconfigure(i, weight=1)
            tarjeta = self._metrica(metricas, titulo, valor, color)
            tarjeta.grid(row=0, column=i, sticky="ew", padx=10, pady=5)
            
        ctk.CTkLabel(self, text="Procesos disponibles", text_color=COLORES["texto"],
                     font=(FUENTE, 18, "bold")).pack(anchor="w", padx=25, pady=(30, 10))
                     
        contenedor = ctk.CTkFrame(self, fg_color="transparent")
        contenedor.pack(fill="x", padx=15)
        
        for i, meta in enumerate(procesos):
            contenedor.grid_columnconfigure(i % 2, weight=1)
            tarjeta = self._proceso(contenedor, meta)
            tarjeta.grid(row=i // 2, column=i % 2, sticky="ew", padx=10, pady=10)

    def _metrica(self, parent, titulo, valor, color):
        card = ctk.CTkFrame(parent, fg_color=COLORES["panel"], corner_radius=8, 
                            border_width=1, border_color=COLORES["borde"])
        
        barra = ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=4)
        barra.pack(fill="x", padx=2, pady=(2, 0))
        
        ctk.CTkLabel(card, text=titulo, text_color=COLORES["texto_secundario"],
                     font=(FUENTE, 13)).pack(anchor="w", padx=20, pady=(15, 0))
        ctk.CTkLabel(card, text=str(valor), text_color=COLORES["texto"],
                     font=(FUENTE, 32, "bold")).pack(anchor="w", padx=20, pady=(0, 15))
        return card

    def _proceso(self, parent, meta):
        card = ctk.CTkFrame(parent, fg_color=COLORES["panel"], corner_radius=8,
                            border_width=1, border_color=COLORES["borde"])
        
        ctk.CTkLabel(card, text=meta.get("nombre", meta.get("id", "Proceso")), 
                     text_color=COLORES["texto"], font=(FUENTE, 15, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(card, text=meta.get("estado", "Disponible"), text_color=COLORES["verde"],
                     font=(FUENTE, 12, "bold")).pack(anchor="w", padx=20)
                     
        ctk.CTkButton(card, text="Abrir →", fg_color="transparent", text_color=COLORES["primario"],
                      hover_color=COLORES["panel_suave"], font=(FUENTE, 13, "bold"),
                      command=lambda: self.on_abrir_proceso and self.on_abrir_proceso(meta["id"])).pack(anchor="e", padx=15, pady=15)
        return card
