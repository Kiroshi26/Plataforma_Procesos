import customtkinter as ctk
from pathlib import Path
from tkinter import messagebox
from interfaz.estilos import COLORES, FUENTE


class PaginaConfiguracion(ctk.CTkScrollableFrame):
    def __init__(self, parent, preferencias, version, total_procesos, on_guardar=None, on_restablecer=None):
        super().__init__(parent, fg_color="transparent")
        self.preferencias = preferencias
        self.on_guardar = on_guardar
        self.on_restablecer = on_restablecer

        self.tema = ctk.StringVar(value=preferencias.obtener("tema", "claro"))
        self.recordar_ventana = ctk.BooleanVar(value=preferencias.obtener("recordar_ventana", True))
        self.recordar_sidebar = ctk.BooleanVar(value=preferencias.obtener("recordar_sidebar", True))
        self.mostrar_consola = ctk.BooleanVar(value=preferencias.obtener("mostrar_consola", True))
        self.confirmar_cierre = ctk.BooleanVar(value=preferencias.obtener("confirmar_cierre", True))
        self.abrir_resultado = ctk.BooleanVar(value=preferencias.obtener("abrir_resultado_automaticamente", False))

        self._construir(version, total_procesos)

    def _construir(self, version, total_procesos):
        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.pack(fill="x", padx=28, pady=(24, 12))
        ctk.CTkLabel(cabecera, text="Configuración", text_color=COLORES["texto"], font=(FUENTE, 28, "bold")).pack(anchor="w")
        ctk.CTkLabel(cabecera, text="Personaliza tu experiencia en el Aplicativo de Procesos.", text_color=COLORES["texto_secundario"], font=(FUENTE, 14)).pack(anchor="w", pady=(3, 0))

        contenido = ctk.CTkFrame(self, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        contenido.grid_columnconfigure((0, 1), weight=1, uniform="config")

        apariencia = self._seccion(contenido, "Apariencia", "Elige cómo quieres ver el aplicativo.")
        apariencia.grid(row=0, column=0, sticky="nsew", padx=7, pady=7)
        selector = ctk.CTkSegmentedButton(
            apariencia,
            values=["Claro", "Oscuro"],
            command=lambda valor: self.tema.set(valor.lower()),
            selected_color=COLORES["primario"],
            selected_hover_color=COLORES["primario_hover"],
            unselected_color=COLORES["panel_suave"],
            unselected_hover_color=COLORES["borde"],
            text_color=COLORES["texto"],
            font=(FUENTE, 12, "bold"),
        )
        selector.pack(fill="x", padx=16, pady=(14, 10))
        selector.set("Claro" if self.tema.get() == "claro" else "Oscuro")
        ctk.CTkLabel(apariencia, text="El tema se guarda para la próxima vez que abras AP.", text_color=COLORES["texto_secundario"], font=(FUENTE, 11), wraplength=430, justify="left").pack(anchor="w", padx=16, pady=(0, 14))

        interfaz = self._seccion(contenido, "Interfaz", "Controla cómo se comporta la ventana.")
        interfaz.grid(row=0, column=1, sticky="nsew", padx=7, pady=7)
        self._switch(interfaz, "Recordar tamaño y posición de la ventana", self.recordar_ventana)
        self._switch(interfaz, "Recordar estado de la barra lateral", self.recordar_sidebar)
        self._switch(interfaz, "Mostrar consola durante la ejecución", self.mostrar_consola)

        comportamiento = self._seccion(contenido, "Comportamiento", "Define acciones automáticas y confirmaciones.")
        comportamiento.grid(row=1, column=0, sticky="nsew", padx=7, pady=7)
        self._switch(comportamiento, "Confirmar cierre si hay un proceso en ejecución", self.confirmar_cierre)
        self._switch(comportamiento, "Abrir resultado automáticamente al finalizar", self.abrir_resultado)

        historial = self._seccion(contenido, "Historial", "Ubicación utilizada para registrar las ejecuciones.")
        historial.grid(row=1, column=1, sticky="nsew", padx=7, pady=7)
        ruta_historial = self.preferencias.obtener("historial", r"C:\Proyectos\pruebas\Historial_AP")
        ctk.CTkLabel(historial, text="Ubicación actual", text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(anchor="w", padx=16, pady=(12, 3))
        ctk.CTkLabel(historial, text=ruta_historial, text_color=COLORES["texto"], font=(FUENTE, 12), wraplength=450, justify="left").pack(anchor="w", padx=16)
        estado = "●  Disponible" if Path(ruta_historial).exists() else "●  Se creará con la primera ejecución"
        ctk.CTkLabel(historial, text=estado, text_color=COLORES["verde"], font=(FUENTE, 11, "bold")).pack(anchor="w", padx=16, pady=(7, 14))

        info = self._seccion(contenido, "Información", "Detalles de esta instalación de AP.")
        info.grid(row=2, column=0, sticky="nsew", padx=7, pady=7)
        datos = ctk.CTkFrame(info, fg_color="transparent")
        datos.pack(fill="x", padx=16, pady=(12, 14))
        ctk.CTkLabel(datos, text="Versión", text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).grid(row=0, column=0, sticky="w", pady=3)
        ctk.CTkLabel(datos, text=str(version), text_color=COLORES["texto"], font=(FUENTE, 12, "bold")).grid(row=0, column=1, sticky="e", pady=3)
        ctk.CTkLabel(datos, text="Procesos registrados", text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).grid(row=1, column=0, sticky="w", pady=3)
        ctk.CTkLabel(datos, text=str(total_procesos), text_color=COLORES["texto"], font=(FUENTE, 12, "bold")).grid(row=1, column=1, sticky="e", pady=3)
        datos.grid_columnconfigure(0, weight=1); datos.grid_columnconfigure(1, weight=1)

        restablecer = self._seccion(contenido, "Restablecer", "Vuelve a la configuración predeterminada.")
        restablecer.grid(row=2, column=1, sticky="nsew", padx=7, pady=7)
        ctk.CTkLabel(restablecer, text="Si algo no queda como esperabas, puedes regresar a los valores iniciales.", text_color=COLORES["texto_secundario"], font=(FUENTE, 11), wraplength=430, justify="left").pack(anchor="w", padx=16, pady=(12, 8))
        ctk.CTkButton(restablecer, text="Restablecer configuración", command=self._restablecer, fg_color=COLORES["panel_suave"], text_color=COLORES["texto"], border_width=1, border_color=COLORES["borde"], hover_color=COLORES["borde"], font=(FUENTE, 11, "bold"), corner_radius=7).pack(anchor="w", padx=16, pady=(0, 14))

        acciones = ctk.CTkFrame(self, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
        acciones.pack(fill="x", padx=27, pady=(6, 24))
        ctk.CTkLabel(acciones, text="Los cambios se guardan para futuras sesiones.", text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(side="left", padx=16, pady=14)
        ctk.CTkButton(acciones, text="Aplicar y guardar", command=self._guardar, fg_color=COLORES["primario"], text_color="#111111", hover_color=COLORES["primario_hover"], font=(FUENTE, 12, "bold"), corner_radius=7, height=38).pack(side="right", padx=14, pady=10)

    def _seccion(self, parent, titulo, subtitulo=""):
        panel = ctk.CTkFrame(parent, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
        ctk.CTkLabel(panel, text=titulo, text_color=COLORES["texto"], font=(FUENTE, 16, "bold")).pack(anchor="w", padx=16, pady=(14, 1))
        if subtitulo:
            ctk.CTkLabel(panel, text=subtitulo, text_color=COLORES["texto_secundario"], font=(FUENTE, 11), wraplength=440, justify="left").pack(anchor="w", padx=16)
        return panel

    def _switch(self, parent, texto, variable):
        ctk.CTkSwitch(parent, text=texto, variable=variable, text_color=COLORES["texto"], font=(FUENTE, 12), progress_color=COLORES["primario"], button_color=("#FFFFFF", "#FFFFFF"), button_hover_color=("#EFEFEF", "#E6E6E6")).pack(anchor="w", fill="x", padx=16, pady=7)

    def _guardar(self):
        datos = {
            "tema": self.tema.get(),
            "recordar_ventana": self.recordar_ventana.get(),
            "recordar_sidebar": self.recordar_sidebar.get(),
            "mostrar_consola": self.mostrar_consola.get(),
            "confirmar_cierre": self.confirmar_cierre.get(),
            "abrir_resultado_automaticamente": self.abrir_resultado.get(),
        }
        self.preferencias.actualizar(datos)
        if self.on_guardar:
            self.on_guardar(datos)
        messagebox.showinfo("Configuración", "Preferencias aplicadas y guardadas correctamente.")

    def _restablecer(self):
        if not messagebox.askyesno("Restablecer", "¿Desea restaurar la configuración predeterminada de AP?"):
            return
        self.preferencias.restablecer()
        if self.on_restablecer:
            self.on_restablecer()
        messagebox.showinfo("Configuración", "Configuración restablecida. Reinicie AP para aplicar todos los cambios.")
