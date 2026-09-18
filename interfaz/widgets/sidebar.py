import customtkinter as ctk
from interfaz.estilos import FUENTE

class Sidebar(ctk.CTkFrame):
    ANCHO_EXPANDIDO = 210
    ANCHO_COLAPSADO = 68

    def __init__(self, parent, on_navegar=None):
        super().__init__(parent, width=self.ANCHO_EXPANDIDO, corner_radius=0, fg_color="transparent")
        self.pack_propagate(False)
        self.on_navegar = on_navegar
        self.colapsada = False
        self.seleccion = "inicio"
        self.botones = {}

        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.pack(fill="x", padx=10, pady=(12, 18))
        
        # Logo placeholder
        ctk.CTkLabel(cabecera, text="AP", fg_color="#2563EB", text_color="white",
                     font=(FUENTE, 14, "bold"), width=32, height=32, corner_radius=6).pack(side="left")
                     
        self.btn_colapsar = ctk.CTkButton(cabecera, text="<", command=self.alternar,
                                        width=28, height=28, corner_radius=14, fg_color="transparent",
                                        hover_color=("gray85", "gray25"), text_color=("gray20", "gray80"),
                                        font=(FUENTE, 16))
        self.btn_colapsar.pack(side="right")
        
        self.opciones = [
            ("inicio", "⌂", "Inicio"),
            ("procesos", "▦", "Procesos"),
            ("monitoreo", "◉", "Monitoreo"),
            ("configuracion", "⚙", "Configuración"),
        ]
        
        for clave, icono, texto in self.opciones:
            boton = ctk.CTkButton(self, text=f"{icono}   {texto}", anchor="w",
                                  fg_color="transparent", text_color=("gray20", "gray90"),
                                  hover_color=("gray85", "gray25"),
                                  font=(FUENTE, 13), height=40, corner_radius=8,
                                  command=lambda c=clave: self.seleccionar(c, notificar=True))
            boton.pack(fill="x", padx=12, pady=3)
            self.botones[clave] = boton
            
        self.seleccionar("inicio", notificar=False)

    def seleccionar(self, clave, notificar=False):
        self.seleccion = clave
        for nombre, boton in self.botones.items():
            activo = nombre == clave
            if activo:
                boton.configure(fg_color=("#EFF6FF", "#1E3A5F"), text_color=("#2563EB", "#60A5FA"), font=(FUENTE, 13, "bold"))
            else:
                boton.configure(fg_color="transparent", text_color=("gray20", "gray90"), font=(FUENTE, 13, "normal"))
                
        if notificar and self.on_navegar:
            self.on_navegar(clave)

    def alternar(self):
        self.colapsada = not self.colapsada
        self.configure(width=self.ANCHO_COLAPSADO if self.colapsada else self.ANCHO_EXPANDIDO)
        self.btn_colapsar.configure(text=">" if self.colapsada else "<")
        
        for clave, icono, texto in self.opciones:
            if self.colapsada:
                self.botones[clave].configure(text=icono, anchor="center")
            else:
                self.botones[clave].configure(text=f"{icono}   {texto}", anchor="w")
