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

        hero = ctk.CTkFrame(self, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
        hero.pack(fill="x", padx=20, pady=(18, 10))
        hero.grid_columnconfigure(0, weight=3); hero.grid_columnconfigure(1, weight=2)
        texto = ctk.CTkFrame(hero, fg_color="transparent"); texto.grid(row=0, column=0, sticky="nsew", padx=22, pady=22)
        ctk.CTkLabel(texto, text="Inicio", text_color=COLORES["texto"], font=(FUENTE, 32, "bold")).pack(anchor="w")
        ctk.CTkLabel(texto, text="Bienvenido al Aplicativo de Procesos", text_color=COLORES["texto"], font=(FUENTE, 20)).pack(anchor="w", pady=(10, 2))
        ctk.CTkLabel(texto, text="Automatizaciones modulares, trazables y protegidas.", text_color=COLORES["texto_secundario"], font=(FUENTE, 13)).pack(anchor="w")
        visual = ctk.CTkFrame(hero, fg_color=COLORES["azul_suave"], corner_radius=10)
        visual.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        ctk.CTkLabel(visual, text="Aplicativo de Procesos", text_color=COLORES["texto"], font=(FUENTE, 17, "bold")).pack(anchor="e", padx=18, pady=(18, 2))
        ctk.CTkLabel(visual, text="Juntos hacemos que\nlas cosas pasen", justify="right", text_color=COLORES["texto"], font=(FUENTE, 15, "bold")).pack(anchor="e", padx=18, pady=(5, 18))

        metricas = ctk.CTkFrame(self, fg_color="transparent"); metricas.pack(fill="x", padx=14, pady=4)
        datos = [
            ("▦", "Procesos", str(len(procesos)), "Total registrados", COLORES["azul_suave"], COLORES["azul"]),
            ("✓", "Disponibles", str(disponibles), "Listos para ejecutar", COLORES["verde_suave"], COLORES["verde"]),
            ("−", "No disponibles", str(len(procesos)-disponibles), "En mantenimiento", COLORES["panel_suave"], COLORES["texto_secundario"]),
            ("◷", "Última ejecución", "Consultar", "Ver en Monitoreo", COLORES["panel"], COLORES["texto"]),
        ]
        for i,d in enumerate(datos):
            metricas.grid_columnconfigure(i,weight=1); self._metrica(metricas,*d).grid(row=0,column=i,sticky="nsew",padx=6,pady=5)

        procesos_panel = ctk.CTkFrame(self, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
        procesos_panel.pack(fill="x", padx=20, pady=(8, 8))
        ctk.CTkLabel(procesos_panel,text="Procesos disponibles",text_color=COLORES["texto"],font=(FUENTE,18,"bold")).pack(anchor="w",padx=16,pady=(14,1))
        ctk.CTkLabel(procesos_panel,text="Selecciona un proceso para comenzar",text_color=COLORES["texto_secundario"],font=(FUENTE,12)).pack(anchor="w",padx=16,pady=(0,8))
        grid=ctk.CTkFrame(procesos_panel,fg_color="transparent"); grid.pack(fill="x",padx=10,pady=(0,12))
        for i,meta in enumerate(procesos): grid.grid_columnconfigure(i%2,weight=1); self._proceso(grid,meta).grid(row=i//2,column=i%2,sticky="nsew",padx=6,pady=6)

        inferior=ctk.CTkFrame(self,fg_color="transparent"); inferior.pack(fill="x",padx=14,pady=(2,8)); inferior.grid_columnconfigure((0,1),weight=1)
        actividad=ctk.CTkFrame(inferior,fg_color=COLORES["panel"],corner_radius=12,border_width=1,border_color=COLORES["borde"]); actividad.grid(row=0,column=0,sticky="nsew",padx=6)
        ctk.CTkLabel(actividad,text="Actividad reciente",text_color=COLORES["texto"],font=(FUENTE,16,"bold")).pack(anchor="w",padx=16,pady=(14,4))
        ctk.CTkLabel(actividad,text="Consulta en Monitoreo el historial y los resultados generados.",wraplength=450,justify="left",text_color=COLORES["texto_secundario"],font=(FUENTE,12)).pack(anchor="w",padx=16,pady=(0,16))
        accesos=ctk.CTkFrame(inferior,fg_color=COLORES["panel"],corner_radius=12,border_width=1,border_color=COLORES["borde"]); accesos.grid(row=0,column=1,sticky="nsew",padx=6)
        ctk.CTkLabel(accesos,text="Accesos rápidos",text_color=COLORES["texto"],font=(FUENTE,16,"bold")).pack(anchor="w",padx=16,pady=(14,4))
        ctk.CTkLabel(accesos,text="Monitoreo  •  Configuración  •  Ayuda",text_color=COLORES["texto_secundario"],font=(FUENTE,12)).pack(anchor="w",padx=16,pady=(3,16))

        seguridad=ctk.CTkFrame(self,fg_color=COLORES["amarillo_suave"],corner_radius=10); seguridad.pack(fill="x",padx=20,pady=(8,20))
        ctk.CTkLabel(seguridad,text="💡  Recuerda mantener tus credenciales seguras y usar los resultados únicamente por canales autorizados.",text_color=COLORES["texto"],font=(FUENTE,11),wraplength=850,justify="left").pack(side="left",fill="x",expand=True,padx=16,pady=12)
        ctk.CTkLabel(seguridad,text="Seguridad   |   Confidencialidad   |   Integridad",text_color=COLORES["texto_secundario"],font=(FUENTE,10)).pack(side="right",padx=16,pady=12)

    def _metrica(self,parent,icono,titulo,valor,detalle,fondo,acento):
        c=ctk.CTkFrame(parent,fg_color=COLORES["panel"],corner_radius=12,border_width=1,border_color=COLORES["borde"])
        icon=ctk.CTkLabel(c,text=icono,width=46,height=46,corner_radius=9,fg_color=fondo,text_color=acento,font=(FUENTE,20,"bold")); icon.pack(side="left",padx=(14,10),pady=14)
        txt=ctk.CTkFrame(c,fg_color="transparent"); txt.pack(side="left",fill="both",expand=True,pady=12)
        ctk.CTkLabel(txt,text=titulo,text_color=COLORES["texto_secundario"],font=(FUENTE,11)).pack(anchor="w")
        ctk.CTkLabel(txt,text=valor,text_color=COLORES["texto"],font=(FUENTE,22,"bold")).pack(anchor="w")
        ctk.CTkLabel(txt,text=detalle,text_color=COLORES["texto_secundario"],font=(FUENTE,10)).pack(anchor="w")
        return c

    def _proceso(self,parent,meta):
        c=ctk.CTkFrame(parent,fg_color=COLORES["panel"],corner_radius=10,border_width=1,border_color=COLORES["borde"])
        cuerpo=ctk.CTkFrame(c,fg_color="transparent"); cuerpo.pack(fill="both",expand=True,padx=14,pady=12)
        ctk.CTkLabel(cuerpo,text=meta.get("nombre",meta.get("id","Proceso")),text_color=COLORES["texto"],font=(FUENTE,16,"bold")).pack(anchor="w")
        ctk.CTkLabel(cuerpo,text=meta.get("descripcion",""),wraplength=430,justify="left",text_color=COLORES["texto_secundario"],font=(FUENTE,11)).pack(anchor="w",pady=(5,7))
        ctk.CTkLabel(cuerpo,text=f"●  {meta.get('estado','Disponible')}",text_color=COLORES["verde"],font=(FUENTE,10,"bold")).pack(anchor="w")
        ctk.CTkButton(cuerpo,text="Abrir módulo  →",fg_color=COLORES["primario"],hover_color=COLORES["primario_hover"],text_color=COLORES["texto_boton"],font=(FUENTE,11,"bold"),command=lambda:self.on_abrir_proceso and self.on_abrir_proceso(meta["id"])).pack(anchor="e",pady=(8,0)); return c
