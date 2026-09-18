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
        ctk.CTkLabel(self, text="Configuración", text_color=COLORES["texto"],
                     font=(FUENTE, 28, "bold")).pack(anchor="w", padx=28, pady=(26, 4))
        ctk.CTkLabel(self, text="Personaliza el comportamiento y apariencia de AP.",
                     text_color=COLORES["texto_secundario"], font=(FUENTE, 14)).pack(anchor="w", padx=28, pady=(0, 18))

        contenido = ctk.CTkFrame(self, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        apariencia = self._seccion(contenido, "Apariencia")
        ctk.CTkRadioButton(apariencia, text="Claro", variable=self.tema, value="claro", text_color=COLORES["texto"]).pack(anchor="w", padx=16, pady=(8, 2))
        ctk.CTkRadioButton(apariencia, text="Oscuro", variable=self.tema, value="oscuro", text_color=COLORES["texto"]).pack(anchor="w", padx=16, pady=(2, 8))
        ctk.CTkLabel(apariencia, text="El cambio de tema se aplica al reiniciar AP.",
                     text_color=COLORES["texto_secundario"], font=(FUENTE, 12)).pack(anchor="w", padx=16, pady=(0, 12))

        interfaz = self._seccion(contenido, "Interfaz")
        self._check(interfaz, "Recordar tamaño y posición de la ventana", self.recordar_ventana)
        self._check(interfaz, "Recordar estado de la barra lateral", self.recordar_sidebar)
        self._check(interfaz, "Mostrar consola durante la ejecución", self.mostrar_consola)

        comportamiento = self._seccion(contenido, "Comportamiento")
        self._check(comportamiento, "Confirmar cierre si hay un proceso en ejecución", self.confirmar_cierre)
        self._check(comportamiento, "Abrir resultado automáticamente al finalizar", self.abrir_resultado)

        historial = self._seccion(contenido, "Historial")
        ruta_historial = self.preferencias.obtener("historial", r"C:\Proyectos\pruebas\Historial_AP")
        ctk.CTkLabel(historial, text="Ubicación temporal", text_color=COLORES["texto_secundario"],
                     font=(FUENTE, 12)).pack(anchor="w", padx=16, pady=(10, 2))
        ctk.CTkLabel(historial, text=ruta_historial, text_color=COLORES["texto"],
                     font=(FUENTE, 13), wraplength=700, justify="left").pack(anchor="w", padx=16)
                     
        estado = "Disponible" if Path(ruta_historial).exists() else "Se creará con la primera ejecución"
        ctk.CTkLabel(historial, text=estado, text_color=COLORES["verde"],
                     font=(FUENTE, 12, "bold")).pack(anchor="w", padx=16, pady=(4, 12))

        info = self._seccion(contenido, "Información")
        ctk.CTkLabel(info, text=f"Versión: {version}    •    Procesos registrados: {total_procesos}",
                     text_color=COLORES["texto_secundario"], font=(FUENTE, 13)).pack(anchor="w", padx=16, pady=12)

        acciones = ctk.CTkFrame(contenido, fg_color="transparent")
        acciones.pack(fill="x", pady=(15, 0))
        
        ctk.CTkButton(acciones, text="Aplicar y guardar", command=self._guardar,
                      fg_color=COLORES["primario"], text_color="white", hover_color=COLORES["primario_hover"],
                      font=(FUENTE, 13, "bold"), corner_radius=6).pack(side="left")
                      
        ctk.CTkButton(acciones, text="Restablecer", command=self._restablecer,
                      fg_color=COLORES["panel_suave"], text_color=COLORES["texto"], border_width=1, border_color=COLORES["borde"],
                      hover_color=COLORES["borde"], font=(FUENTE, 13), corner_radius=6).pack(side="left", padx=15)

    def _seccion(self, parent, titulo):
        panel = ctk.CTkFrame(parent, fg_color=COLORES["panel"], corner_radius=8,
                             border_width=1, border_color=COLORES["borde"])
        panel.pack(fill="x", pady=8)
        ctk.CTkLabel(panel, text=titulo, text_color=COLORES["texto"],
                     font=(FUENTE, 16, "bold")).pack(anchor="w", padx=16, pady=(12, 2))
        return panel

    def _check(self, parent, texto, variable):
        ctk.CTkCheckBox(parent, text=texto, variable=variable, text_color=COLORES["texto"], font=(FUENTE, 13)).pack(anchor="w", padx=16, pady=6)

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
