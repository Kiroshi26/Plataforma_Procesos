import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from interfaz.estilos import COLORES, FUENTE


class PaginaConfiguracion(tk.Frame):
    def __init__(self, parent, preferencias, version, total_procesos, on_guardar=None, on_restablecer=None):
        super().__init__(parent, bg=COLORES["fondo"])
        self.preferencias = preferencias
        self.on_guardar = on_guardar
        self.on_restablecer = on_restablecer

        self.tema = tk.StringVar(value=preferencias.obtener("tema", "claro"))
        self.recordar_ventana = tk.BooleanVar(value=preferencias.obtener("recordar_ventana", True))
        self.recordar_sidebar = tk.BooleanVar(value=preferencias.obtener("recordar_sidebar", True))
        self.mostrar_consola = tk.BooleanVar(value=preferencias.obtener("mostrar_consola", True))
        self.confirmar_cierre = tk.BooleanVar(value=preferencias.obtener("confirmar_cierre", True))
        self.abrir_resultado = tk.BooleanVar(value=preferencias.obtener("abrir_resultado_automaticamente", False))

        self._construir(version, total_procesos)

    def _construir(self, version, total_procesos):
        tk.Label(self, text="Configuración", bg=COLORES["fondo"], fg=COLORES["texto"],
                 font=(FUENTE, 22, "bold")).pack(anchor="w", padx=28, pady=(26, 4))
        tk.Label(self, text="Personaliza el comportamiento y apariencia de AP.", bg=COLORES["fondo"],
                 fg=COLORES["texto_secundario"], font=(FUENTE, 10)).pack(anchor="w", padx=28, pady=(0, 18))

        contenido = tk.Frame(self, bg=COLORES["fondo"])
        contenido.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        apariencia = self._seccion(contenido, "Apariencia")
        ttk.Radiobutton(apariencia, text="Claro", variable=self.tema, value="claro").pack(anchor="w", padx=16, pady=(8, 2))
        ttk.Radiobutton(apariencia, text="Oscuro", variable=self.tema, value="oscuro").pack(anchor="w", padx=16, pady=(2, 8))
        tk.Label(apariencia, text="El cambio de tema se aplica al reiniciar AP.", bg=COLORES["panel"],
                 fg=COLORES["texto_secundario"], font=(FUENTE, 9)).pack(anchor="w", padx=16, pady=(0, 12))

        interfaz = self._seccion(contenido, "Interfaz")
        self._check(interfaz, "Recordar tamaño y posición de la ventana", self.recordar_ventana)
        self._check(interfaz, "Recordar estado de la barra lateral", self.recordar_sidebar)
        self._check(interfaz, "Mostrar consola durante la ejecución", self.mostrar_consola)

        comportamiento = self._seccion(contenido, "Comportamiento")
        self._check(comportamiento, "Confirmar cierre si hay un proceso en ejecución", self.confirmar_cierre)
        self._check(comportamiento, "Abrir resultado automáticamente al finalizar", self.abrir_resultado)

        historial = self._seccion(contenido, "Historial")
        ruta_historial = preferencias_ruta = self.preferencias.obtener("historial", r"C:\Proyectos\pruebas\Historial_AP")
        tk.Label(historial, text="Ubicación temporal", bg=COLORES["panel"], fg=COLORES["texto_secundario"],
                 font=(FUENTE, 9)).pack(anchor="w", padx=16, pady=(10, 2))
        tk.Label(historial, text=ruta_historial, bg=COLORES["panel"], fg=COLORES["texto"],
                 font=(FUENTE, 9), wraplength=700, justify="left").pack(anchor="w", padx=16)
        estado = "Disponible" if Path(preferencias_ruta).exists() else "Se creará con la primera ejecución"
        tk.Label(historial, text=estado, bg=COLORES["panel"], fg=COLORES["verde"],
                 font=(FUENTE, 9, "bold")).pack(anchor="w", padx=16, pady=(4, 12))

        info = self._seccion(contenido, "Información")
        tk.Label(info, text=f"Versión: {version}    •    Procesos registrados: {total_procesos}",
                 bg=COLORES["panel"], fg=COLORES["texto_secundario"], font=(FUENTE, 9)).pack(anchor="w", padx=16, pady=12)

        acciones = tk.Frame(contenido, bg=COLORES["fondo"])
        acciones.pack(fill="x", pady=(8, 0))
        tk.Button(acciones, text="Aplicar y guardar", command=self._guardar, relief="flat", bd=0,
                  bg=COLORES["primario"], fg="white", activebackground=COLORES["primario_hover"],
                  activeforeground="white", font=(FUENTE, 9, "bold"), padx=14, pady=8).pack(side="left")
        tk.Button(acciones, text="Restablecer", command=self._restablecer, relief="flat", bd=0,
                  bg=COLORES["panel_suave"], fg=COLORES["texto"], font=(FUENTE, 9), padx=14, pady=8).pack(side="left", padx=8)

    def _seccion(self, parent, titulo):
        panel = tk.Frame(parent, bg=COLORES["panel"], highlightbackground=COLORES["borde"], highlightthickness=1)
        panel.pack(fill="x", pady=5)
        tk.Label(panel, text=titulo, bg=COLORES["panel"], fg=COLORES["texto"],
                 font=(FUENTE, 11, "bold")).pack(anchor="w", padx=16, pady=(12, 2))
        return panel

    def _check(self, parent, texto, variable):
        ttk.Checkbutton(parent, text=texto, variable=variable).pack(anchor="w", padx=16, pady=4)

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
