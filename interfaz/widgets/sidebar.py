import customtkinter as ctk
from interfaz.estilos import COLORES, FUENTE

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, on_navegar=None):
        super().__init__(parent, fg_color=COLORES["sidebar"], corner_radius=0)
        self.on_navegar = on_navegar
        self.botones = {}
        self.colapsada = False

        self._construir()

    def _construir(self):
        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.pack(fill="x", padx=16, pady=(20, 30))

        # Logo text Bancolombia
        self.etiqueta_logo = ctk.CTkLabel(
            cabecera, text="☰ Bancolombia", 
            text_color=COLORES["blanco"], font=(FUENTE, 18, "bold")
        )
        self.etiqueta_logo.pack(anchor="w", padx=6)
        
        self.etiqueta_sub = ctk.CTkLabel(
            cabecera, text="Aplicativo de Procesos", 
            text_color=COLORES["amarillo"], font=(FUENTE, 10, "bold")
        )
        self.etiqueta_sub.pack(anchor="w", padx=28)

        opciones = [
            ("inicio", "🏠", "Inicio"),
            ("procesos", "▦", "Procesos"),
            ("monitoreo", "📊", "Monitoreo"),
            ("configuracion", "⚙", "Configuración"),
        ]

        self.contenedor_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_botones.pack(fill="x", pady=10)

        for id_opcion, icono, texto in opciones:
            boton = ctk.CTkButton(
                self.contenedor_botones, text=f"  {icono}    {texto}", anchor="w",
                fg_color="transparent", text_color=COLORES["sidebar_texto"], 
                hover_color="#333333", font=(FUENTE, 13), height=40, corner_radius=8,
                command=lambda op=id_opcion: self._al_clic(op)
            )
            boton.pack(fill="x", padx=12, pady=4)
            self.botones[id_opcion] = boton

        # Bottom graphic area
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="y", expand=True)

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", pady=(0, 0))
        
        # Simple graphic representation
        curve = ctk.CTkLabel(bottom_frame, text="", bg_color=COLORES["amarillo"], height=4)
        curve.pack(fill="x")
        
        self.etiqueta_juntos = ctk.CTkLabel(
            bottom_frame, text="Juntos\nhacemos que\nlas cosas pasen", 
            text_color=COLORES["blanco"], font=(FUENTE, 12), justify="left"
        )
        self.etiqueta_juntos.pack(anchor="w", padx=20, pady=20)

    def _al_clic(self, id_opcion):
        if self.on_navegar:
            self.on_navegar(id_opcion)

    def seleccionar(self, id_opcion, notificar=True):
        for op, boton in self.botones.items():
            if op == id_opcion:
                boton.configure(fg_color=COLORES["sidebar_activo"], text_color=COLORES["sidebar_texto_activo"], hover_color=COLORES["primario_hover"], font=(FUENTE, 13, "bold"))
            else:
                boton.configure(fg_color="transparent", text_color=COLORES["sidebar_texto"], hover_color="#333333", font=(FUENTE, 13, "normal"))
        if notificar and self.on_navegar:

            self.on_navegar(clave)

            self.on_navegar(id_opcion)

    def alternar(self):
        # We don't implement collapse for the redesign since the mockup shows a full fixed sidebar
        pass
