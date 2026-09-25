import getpass
import os
import subprocess
import sys
import customtkinter as ctk
from pathlib import Path
from tkinter import messagebox

from interfaz.estilos import COLORES, FUENTE

class PaginaMonitoreo(ctk.CTkFrame):
    def __init__(self, parent, historial):
        super().__init__(parent, fg_color="transparent")
        self.historial = historial
        self.modo = ctk.StringVar(value="todas")
        self.filtro_proceso = ctk.StringVar(value="Todos")
        self.filtro_estado = ctk.StringVar(value="Todos")
        self._registros_cache = None
        self._firma_cache = None
        self._construir_interfaz()
        self.actualizar(forzar=True)

    def _construir_interfaz(self):
        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.pack(fill="x", padx=28, pady=(26, 14))

        ctk.CTkLabel(cabecera, text="Monitoreo", text_color=COLORES["texto"],
                     font=(FUENTE, 28, "bold")).pack(anchor="w")

        ctk.CTkLabel(cabecera, text="Historial de ejecuciones y resultados generados.",
                     text_color=COLORES["texto_secundario"], font=(FUENTE, 14)).pack(anchor="w", pady=(4, 0))

        controles = ctk.CTkFrame(self, fg_color="transparent")
        controles.pack(fill="x", padx=28, pady=(0, 12))

        ctk.CTkRadioButton(controles, text="Todas", variable=self.modo, value="todas", 
                           command=lambda: self.actualizar(forzar=True), text_color=COLORES["texto"]).pack(side="left")

        ctk.CTkRadioButton(controles, text="Mis ejecuciones", variable=self.modo, value="mias", 
                           command=lambda: self.actualizar(forzar=True), text_color=COLORES["texto"]).pack(side="left", padx=(15, 25))

        ctk.CTkLabel(controles, text="Proceso:", text_color=COLORES["texto_secundario"]).pack(side="left")

        self.cmb_proceso = ctk.CTkOptionMenu(controles, variable=self.filtro_proceso,
                                             command=lambda _: self.actualizar(forzar=True),
                                             fg_color=COLORES["panel"], text_color=COLORES["texto"],
                                             button_color=COLORES["primario"], button_hover_color=COLORES["primario_hover"])
        self.cmb_proceso.pack(side="left", padx=(8, 20))

        ctk.CTkLabel(controles, text="Estado:", text_color=COLORES["texto_secundario"]).pack(side="left")

        self.cmb_estado = ctk.CTkOptionMenu(controles, variable=self.filtro_estado,
                                            values=["Todos", "FINALIZADO", "ERROR", "EJECUTANDO"],
                                            command=lambda _: self.actualizar(forzar=True),
                                            fg_color=COLORES["panel"], text_color=COLORES["texto"],
                                            button_color=COLORES["primario"], button_hover_color=COLORES["primario_hover"])
        self.cmb_estado.pack(side="left", padx=(8, 0))

        self.lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.lista.pack(fill="both", expand=True, padx=20, pady=(0, 22))

    def actualizar(self, forzar=False):
        usuario = getpass.getuser() if self.modo.get() == "mias" else None
        registros = self.historial.listar(solo_usuario=usuario)
        firma = tuple(
            (r.get("id"), r.get("estado"), r.get("fin"), tuple(r.get("archivos_generados", []) or []))
            for r in registros
        )
        firma = (self.modo.get(), self.filtro_proceso.get(), self.filtro_estado.get(), firma)
        if not forzar and firma == self._firma_cache:
            return
        self._firma_cache = firma
        self._registros_cache = registros

        for widget in self.lista.winfo_children():
            widget.destroy()

        procesos = ["Todos"] + sorted({r.get("proceso_nombre", "Proceso") for r in registros})
        self.cmb_proceso.configure(values=procesos)
        if self.filtro_proceso.get() not in procesos:
            self.filtro_proceso.set("Todos")

        proceso = self.filtro_proceso.get()
        estado = self.filtro_estado.get()
        filtrados = [
            r for r in registros
            if (proceso == "Todos" or r.get("proceso_nombre") == proceso)
            and (estado == "Todos" or r.get("estado") == estado)
        ]

        if not filtrados:
            self._mostrar_sin_ejecuciones()
            return

        for registro in filtrados:
            self._crear_tarjeta(registro).pack(fill="x", pady=5)

    def _mostrar_sin_ejecuciones(self):
        panel = ctk.CTkFrame(self.lista, fg_color=COLORES["panel"], corner_radius=8,
                             border_width=1, border_color=COLORES["borde"])
        panel.pack(fill="x", pady=8)
        
        ctk.CTkLabel(panel, text="No hay ejecuciones para mostrar", text_color=COLORES["texto"],
                     font=(FUENTE, 16, "bold")).pack(anchor="w", padx=20, pady=(20, 4))
        ctk.CTkLabel(panel, text="Las próximas ejecuciones realizadas desde AP aparecerán automáticamente aquí.",
                     text_color=COLORES["texto_secundario"], font=(FUENTE, 13)).pack(anchor="w", padx=20, pady=(0, 20))

    def _crear_tarjeta(self, registro):
        tarjeta = ctk.CTkFrame(self.lista, fg_color=COLORES["panel"], corner_radius=8,
                               border_width=1, border_color=COLORES["borde"])

        estado = str(registro.get("estado", ""))
        if registro.get("exitoso"):
            color_estado = COLORES["verde"]
        elif estado == "ERROR":
            color_estado = COLORES["rojo"]
        else:
            color_estado = COLORES["amarillo"]

        borde_izq = ctk.CTkFrame(tarjeta, fg_color=color_estado, width=6, corner_radius=0)
        borde_izq.pack(side="left", fill="y")

        cuerpo = ctk.CTkFrame(tarjeta, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=20, pady=16)

        superior = ctk.CTkFrame(cuerpo, fg_color="transparent")
        superior.pack(fill="x")

        ctk.CTkLabel(superior, text=registro.get("proceso_nombre", "Proceso"), text_color=COLORES["texto"],
                     font=(FUENTE, 15, "bold")).pack(side="left")
        ctk.CTkLabel(superior, text=estado, text_color=color_estado,
                     font=(FUENTE, 13, "bold")).pack(side="right")

        inicio = str(registro.get("inicio", "")).replace("T", " ")
        duracion = self._formatear_duracion(registro.get("duracion_segundos"))
        detalle = f"{inicio}   •   Usuario: {registro.get('usuario', '')}   •   Duración: {duracion}"
        
        ctk.CTkLabel(cuerpo, text=detalle, text_color=COLORES["texto_secundario"],
                     font=(FUENTE, 13)).pack(anchor="w", pady=(8, 4))

        mensaje = registro.get("mensaje", "")
        if mensaje:
            ctk.CTkLabel(cuerpo, text=mensaje, text_color=COLORES["texto_secundario"],
                         wraplength=800, justify="left", font=(FUENTE, 13)).pack(anchor="w")

        acciones = ctk.CTkFrame(cuerpo, fg_color="transparent")
        acciones.pack(fill="x", pady=(12, 0))

        archivos = registro.get("archivos_generados", []) or []
        if archivos:
            primer_archivo = archivos[0]
            ctk.CTkButton(acciones, text="Abrir archivo", fg_color=COLORES["primario"], text_color=COLORES["texto_boton"],
                          hover_color=COLORES["primario_hover"], font=(FUENTE, 12, "bold"),
                          corner_radius=6, command=lambda ruta=primer_archivo: self._abrir_archivo(ruta)).pack(side="left")

            ctk.CTkButton(acciones, text="Abrir carpeta", fg_color=COLORES["panel_suave"], text_color=COLORES["texto"],
                          font=(FUENTE, 12), corner_radius=6, border_width=1, border_color=COLORES["borde"],
                          hover_color=COLORES["borde"],
                          command=lambda ruta=primer_archivo: self._abrir_carpeta(ruta)).pack(side="left", padx=10)

        ctk.CTkButton(acciones, text="Detalles", fg_color=COLORES["panel_suave"], text_color=COLORES["texto"],
                      font=(FUENTE, 12), corner_radius=6, border_width=1, border_color=COLORES["borde"],
                      hover_color=COLORES["borde"],
                      command=lambda dato=registro: self._mostrar_detalles(dato)).pack(side="right")

        return tarjeta

    @staticmethod
    def _formatear_duracion(segundos):
        if segundos is None: return "En curso"
        segundos = int(segundos)
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos_restantes = segundos % 60
        return f"{horas:02d}:{minutos:02d}:{segundos_restantes:02d}"

    def _abrir_archivo(self, ruta):
        archivo = Path(ruta)
        if not archivo.exists():
            messagebox.showwarning("Archivo", f"El archivo ya no existe:\n\n{archivo}")
            return
        self._abrir(archivo)

    def _abrir_carpeta(self, ruta):
        ruta = Path(ruta)
        carpeta = ruta if ruta.is_dir() else ruta.parent
        if not carpeta.exists():
            messagebox.showwarning("Carpeta", f"La carpeta ya no existe:\n\n{carpeta}")
            return
        self._abrir(carpeta)

    @staticmethod
    def _abrir(ruta):
        try:
            if os.name == "nt":
                os.startfile(str(ruta))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(ruta)])
            else:
                subprocess.Popen(["xdg-open", str(ruta)])
        except Exception as error:
            messagebox.showerror("Abrir", str(error))

    def _mostrar_detalles(self, registro):
        lineas = [
            f"Proceso: {registro.get('proceso_nombre', '')}",
            f"Usuario: {registro.get('usuario', '')}",
            f"Equipo: {registro.get('equipo', '')}",
            f"Inicio: {registro.get('inicio', '')}",
            f"Fin: {registro.get('fin') or 'En curso'}",
            f"Estado: {registro.get('estado', '')}",
            f"Mensaje: {registro.get('mensaje', '')}",
        ]
        advertencias = registro.get("advertencias", []) or []
        errores = registro.get("errores", []) or []
        archivos = registro.get("archivos_generados", []) or []

        if advertencias: lineas.append("\nAdvertencias:\n- " + "\n- ".join(map(str, advertencias)))
        if errores: lineas.append("\nErrores:\n- " + "\n- ".join(map(str, errores)))
        if archivos: lineas.append("\nArchivos generados:\n- " + "\n- ".join(map(str, archivos)))

        messagebox.showinfo("Detalle de ejecución", "\n".join(lineas))
