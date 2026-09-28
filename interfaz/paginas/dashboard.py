import customtkinter as ctk
from interfaz.estilos import COLORES, FUENTE


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

        # Banner Header (Fondo claro con título)
        hero = ctk.CTkFrame(self, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
        hero.pack(fill="x", padx=20, pady=(20, 15))
        hero.grid_columnconfigure(0, weight=1)
        hero.grid_columnconfigure(1, weight=0)

        # Usar colores grises corporativos para simular la imagen de fondo del banner
        texto = ctk.CTkFrame(hero, fg_color="transparent")
        texto.grid(row=0, column=0, sticky="nsew", padx=26, pady=26)
        ctk.CTkLabel(texto, text="Inicio", text_color=COLORES["texto"], font=(FUENTE, 32, "bold")).pack(anchor="w")
        ctk.CTkLabel(texto, text="Bienvenido al Aplicativo de Procesos", text_color=COLORES["texto"], font=(FUENTE, 20)).pack(anchor="w", pady=(8, 2))
        ctk.CTkLabel(texto, text="Automatizaciones modulares, trazables y protegidas.", text_color=COLORES["texto_secundario"], font=(FUENTE, 14)).pack(anchor="w")
        
        # Version top right
        version_frame = ctk.CTkFrame(hero, fg_color="transparent")
        version_frame.grid(row=0, column=1, sticky="ne", padx=20, pady=20)
        ctk.CTkLabel(version_frame, text="Versión 0.4.0", text_color=COLORES["texto_secundario"], font=(FUENTE, 12)).pack()

        # Métricas
        metricas = ctk.CTkFrame(self, fg_color="transparent")
        metricas.pack(fill="x", padx=16, pady=5)
        datos = [
            ("▦", "Procesos", str(len(procesos)), "Total registrados"),
            ("✓", "Disponibles", str(disponibles), "Listos para ejecutar"),
            ("−", "No disponibles", str(len(procesos)-disponibles), "En mantenimiento"),
            ("⏱", "Última ejecución", "Hoy, 11:51", "Comisiones 250115"),
        ]
        for i, d in enumerate(datos):
            metricas.grid_columnconfigure(i, weight=1)
            self._tarjeta_metrica(metricas, *d).grid(row=0, column=i, sticky="nsew", padx=4)

        # Procesos Disponibles
        seccion_proc = ctk.CTkFrame(self, fg_color="transparent")
        seccion_proc.pack(fill="x", padx=20, pady=(25, 10))
        ctk.CTkLabel(seccion_proc, text="Procesos disponibles", text_color=COLORES["texto"], font=(FUENTE, 18, "bold")).pack(anchor="w")
        ctk.CTkLabel(seccion_proc, text="Selecciona un proceso para comenzar", text_color=COLORES["texto_secundario"], font=(FUENTE, 13)).pack(anchor="w")

        grid_proc = ctk.CTkFrame(self, fg_color="transparent")
        grid_proc.pack(fill="x", padx=16)
        
        for i, meta in enumerate(procesos):
            grid_proc.grid_columnconfigure(i % 2, weight=1)
            self._tarjeta_proceso(grid_proc, meta).grid(row=i // 2, column=i % 2, sticky="nsew", padx=4, pady=4)

        # Inferior: Actividad y Accesos
        inferior = ctk.CTkFrame(self, fg_color="transparent")
        inferior.pack(fill="x", padx=16, pady=(15, 20))
        inferior.grid_columnconfigure(0, weight=1)
        inferior.grid_columnconfigure(1, weight=1)

        actividad = ctk.CTkFrame(inferior, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
        actividad.grid(row=0, column=0, sticky="nsew", padx=4)
        
        cabecera_act = ctk.CTkFrame(actividad, fg_color="transparent")
        cabecera_act.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(cabecera_act, text="Actividad reciente", text_color=COLORES["texto"], font=(FUENTE, 16, "bold")).pack(side="left")
        ctk.CTkLabel(cabecera_act, text="Ver todo →", text_color=COLORES["azul"], font=(FUENTE, 12)).pack(side="right")
        
        self._item_actividad(actividad, "Comisiones 250115", "Finalizado con advertencias", "Hoy, 11:51", "Duración: 00:02:05")
        self._item_actividad(actividad, "Inversiones", "Finalizado correctamente", "Ayer, 16:23", "Duración: 00:04:12")

        accesos = ctk.CTkFrame(inferior, fg_color="transparent")
        accesos.grid(row=0, column=1, sticky="nsew", padx=4)
        ctk.CTkLabel(accesos, text="Accesos rápidos", text_color=COLORES["texto"], font=(FUENTE, 16, "bold")).pack(anchor="w", padx=4, pady=(0, 10))
        
        grid_acc = ctk.CTkFrame(accesos, fg_color="transparent")
        grid_acc.pack(fill="both", expand=True)
        for c in range(3): grid_acc.grid_columnconfigure(c, weight=1)
        
        self._tarjeta_acceso(grid_acc, "📊", "Monitoreo", "Historial y resultados").grid(row=0, column=0, sticky="nsew", padx=4)
        self._tarjeta_acceso(grid_acc, "⚙", "Configuración", "Personaliza tu experiencia").grid(row=0, column=1, sticky="nsew", padx=4)
        self._tarjeta_acceso(grid_acc, "❓", "Ayuda", "Documentación y soporte").grid(row=0, column=2, sticky="nsew", padx=4)

    def _tarjeta_metrica(self, parent, icono, titulo, valor, detalle):
        c = ctk.CTkFrame(parent, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
        
        icon_bg = COLORES["fondo_icono_gris"]
        icon_fg = COLORES["icono_gris"]
        if "✓" in icono:
            icon_bg = COLORES["fondo_pill_verde"]
            icon_fg = COLORES["verde"]
        
        icon = ctk.CTkLabel(c, text=icono, width=42, height=42, corner_radius=10, fg_color=icon_bg, text_color=icon_fg, font=(FUENTE, 20, "bold"))
        icon.pack(side="left", padx=(16, 14), pady=16)
        
        txt = ctk.CTkFrame(c, fg_color="transparent")
        txt.pack(side="left", fill="both", expand=True, pady=16)
        ctk.CTkLabel(txt, text=titulo, text_color=COLORES["texto_secundario"], font=(FUENTE, 12)).pack(anchor="w")
        ctk.CTkLabel(txt, text=valor, text_color=COLORES["texto"], font=(FUENTE, 24, "bold")).pack(anchor="w", pady=(0, 2))
        
        b = ctk.CTkFrame(txt, fg_color="transparent")
        b.pack(fill="x")
        ctk.CTkLabel(b, text=detalle, text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(side="left")
        if "⏱" in icono:
            ctk.CTkLabel(b, text=">", text_color=COLORES["texto_secundario"], font=(FUENTE, 14)).pack(side="right", padx=(0, 10))
            
        return c

    def _tarjeta_proceso(self, parent, meta):
        c = ctk.CTkFrame(parent, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
        
        # Icon section
        icon_frame = ctk.CTkFrame(c, fg_color="transparent")
        icon_frame.pack(side="left", fill="y", padx=(20, 10), pady=20)
        
        icono_txt = "🪙" if "comision" in meta["id"].lower() else "📊"
        ctk.CTkLabel(icon_frame, text=icono_txt, width=70, height=70, corner_radius=12, fg_color=COLORES["fondo_modulo"], text_color=COLORES["texto"], font=(FUENTE, 32)).pack()
        
        # Text section
        txt = ctk.CTkFrame(c, fg_color="transparent")
        txt.pack(side="left", fill="both", expand=True, pady=20, padx=10)
        
        ctk.CTkLabel(txt, text=meta.get("nombre", meta.get("id", "Proceso")), text_color=COLORES["texto"], font=(FUENTE, 16, "bold")).pack(anchor="w")
        
        pill = ctk.CTkLabel(txt, text="INTEGRADO" if "comision" in meta["id"].lower() else "DISPONIBLE", 
                            fg_color=COLORES["fondo_pill_verde"], text_color=COLORES["verde"], 
                            font=(FUENTE, 10, "bold"), corner_radius=4, height=20, width=70)
        pill.pack(anchor="w", pady=(4, 6))
        
        ctk.CTkLabel(txt, text=meta.get("descripcion", ""), wraplength=300, justify="left", text_color=COLORES["texto_secundario"], font=(FUENTE, 12)).pack(anchor="w", pady=(0, 10))
        
        ctk.CTkButton(txt, text="Abrir módulo →", fg_color=COLORES["primario"], hover_color=COLORES["primario_hover"], text_color=COLORES["texto_boton"], font=(FUENTE, 12, "bold"), width=120, height=32, corner_radius=6, command=lambda: self.on_abrir_proceso and self.on_abrir_proceso(meta["id"])).pack(anchor="w")
        
        # Arrow right
        arr = ctk.CTkFrame(c, fg_color="transparent")
        arr.pack(side="right", fill="y", padx=20)
        ctk.CTkLabel(arr, text=">", text_color=COLORES["texto_secundario"], font=(FUENTE, 18)).pack(expand=True)
        
        return c

    def _item_actividad(self, parent, titulo, estado, fecha, duracion):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=10)
        
        icon = ctk.CTkLabel(f, text="✓", width=28, height=28, corner_radius=14, fg_color=COLORES["verde"], text_color=COLORES["blanco"], font=(FUENTE, 14, "bold"))
        icon.pack(side="left")
        
        txt1 = ctk.CTkFrame(f, fg_color="transparent")
        txt1.pack(side="left", fill="y", padx=14)
        ctk.CTkLabel(txt1, text=titulo, text_color=COLORES["texto"], font=(FUENTE, 13, "bold")).pack(anchor="w")
        ctk.CTkLabel(txt1, text=estado, text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(anchor="w")
        
        txt2 = ctk.CTkFrame(f, fg_color="transparent")
        txt2.pack(side="right", fill="y")
        ctk.CTkLabel(txt2, text=fecha, text_color=COLORES["texto_secundario"], font=(FUENTE, 12)).pack(anchor="e")
        ctk.CTkLabel(txt2, text=duracion, text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(anchor="e")
        
    def _tarjeta_acceso(self, parent, icono, titulo, sub):
        c = ctk.CTkFrame(parent, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
        ctk.CTkLabel(c, text=icono, width=50, height=50, corner_radius=25, fg_color=COLORES["fondo_pill_verde"], text_color=COLORES["verde"], font=(FUENTE, 24)).pack(pady=(20, 10))
        ctk.CTkLabel(c, text=titulo, text_color=COLORES["texto"], font=(FUENTE, 14, "bold")).pack()
        ctk.CTkLabel(c, text=sub, text_color=COLORES["texto_secundario"], font=(FUENTE, 11), wraplength=120, justify="center").pack(pady=(2, 20))
        return c
