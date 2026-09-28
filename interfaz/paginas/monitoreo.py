import getpass
import os
import subprocess
import sys
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from interfaz.estilos import COLORES, FUENTE


class PaginaMonitoreo(ctk.CTkFrame):
    def __init__(self, parent, historial):
        super().__init__(parent, fg_color="transparent")
        self.historial = historial
        self.modo = ctk.StringVar(value="todas")
        self.filtro_proceso = ctk.StringVar(value="Todos")
        self.filtro_estado = ctk.StringVar(value="Todos")
        self._firma_cache = None
        self._construir_interfaz()
        self.actualizar(forzar=True)

    def _construir_interfaz(self):
        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.pack(fill="x", padx=28, pady=(24, 12))
        ctk.CTkLabel(cabecera, text="Monitoreo", text_color=COLORES["texto"], font=(FUENTE, 30, "bold")).pack(anchor="w")
        ctk.CTkLabel(cabecera, text="Historial, estado y resultados de las ejecuciones.", text_color=COLORES["texto_secundario"], font=(FUENTE, 14)).pack(anchor="w", pady=(3, 0))

        self.resumen = ctk.CTkFrame(self, fg_color="transparent")
        self.resumen.pack(fill="x", padx=22, pady=(0, 10))
        for columna in range(4):
            self.resumen.grid_columnconfigure(columna, weight=1, uniform="monitoreo")

        filtros = ctk.CTkFrame(self, fg_color=COLORES["panel"], corner_radius=14, border_width=1, border_color=COLORES["borde"])
        filtros.pack(fill="x", padx=28, pady=(0, 12))

        izquierda = ctk.CTkFrame(filtros, fg_color="transparent")
        izquierda.pack(side="left", padx=14, pady=12)
        ctk.CTkRadioButton(izquierda, text="Todas", variable=self.modo, value="todas", command=lambda: self.actualizar(forzar=True), text_color=COLORES["texto"], fg_color=COLORES["primario"], hover_color=COLORES["primario_hover"]).pack(side="left")
        ctk.CTkRadioButton(izquierda, text="Mis ejecuciones", variable=self.modo, value="mias", command=lambda: self.actualizar(forzar=True), text_color=COLORES["texto"], fg_color=COLORES["primario"], hover_color=COLORES["primario_hover"]).pack(side="left", padx=(16, 0))

        derecha = ctk.CTkFrame(filtros, fg_color="transparent")
        derecha.pack(side="right", padx=14, pady=10)
        ctk.CTkLabel(derecha, text="Proceso", text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(side="left", padx=(0, 6))
        self.cmb_proceso = ctk.CTkOptionMenu(derecha, variable=self.filtro_proceso, command=lambda _: self.actualizar(forzar=True), fg_color=COLORES["panel_suave"], text_color=COLORES["texto"], button_color=COLORES["primario"], button_hover_color=COLORES["primario_hover"])
        self.cmb_proceso.pack(side="left", padx=(0, 14))
        ctk.CTkLabel(derecha, text="Estado", text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(side="left", padx=(0, 6))
        self.cmb_estado = ctk.CTkOptionMenu(derecha, variable=self.filtro_estado, values=["Todos", "FINALIZADO", "FINALIZADO CON ADVERTENCIAS", "ERROR", "EJECUTANDO"], command=lambda _: self.actualizar(forzar=True), fg_color=COLORES["panel_suave"], text_color=COLORES["texto"], button_color=COLORES["primario"], button_hover_color=COLORES["primario_hover"])
        self.cmb_estado.pack(side="left")

        ctk.CTkLabel(self, text="Historial de ejecuciones", text_color=COLORES["texto"], font=(FUENTE, 18, "bold")).pack(anchor="w", padx=28, pady=(4, 7))
        self.lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.lista.pack(fill="both", expand=True, padx=20, pady=(0, 22))

    def actualizar(self, forzar=False):
        usuario = getpass.getuser() if self.modo.get() == "mias" else None
        registros = self.historial.listar(solo_usuario=usuario)

        firma_registros = tuple((r.get("id"), r.get("estado"), r.get("fin"), r.get("duracion_segundos"), tuple(r.get("archivos_generados", []) or [])) for r in registros)
        firma = (self.modo.get(), self.filtro_proceso.get(), self.filtro_estado.get(), firma_registros)
        if not forzar and firma == self._firma_cache:
            return
        self._firma_cache = firma

        for widget in self.lista.winfo_children():
            widget.destroy()
        for widget in self.resumen.winfo_children():
            widget.destroy()

        procesos = ["Todos"] + sorted({r.get("proceso_nombre", "Proceso") for r in registros})
        self.cmb_proceso.configure(values=procesos)
        if self.filtro_proceso.get() not in procesos:
            self.filtro_proceso.set("Todos")

        proceso = self.filtro_proceso.get()
        estado = self.filtro_estado.get()
        filtrados = [r for r in registros if (proceso == "Todos" or r.get("proceso_nombre") == proceso) and (estado == "Todos" or r.get("estado") == estado)]

        ejecutando = sum(1 for r in registros if r.get("estado") == "EJECUTANDO")
        exitosos = sum(1 for r in registros if r.get("exitoso") is True)
        alertas = sum(1 for r in registros if "ADVERT" in str(r.get("estado", "")).upper() or bool(r.get("advertencias")))
        errores = sum(1 for r in registros if r.get("estado") == "ERROR" or r.get("exitoso") is False)

        datos = [
            ("◉", "Ejecutando", ejecutando, "Procesos activos", COLORES["azul_suave"], COLORES["azul"]),
            ("✓", "Exitosos", exitosos, "Finalizados correctamente", COLORES["verde_suave"], COLORES["verde"]),
            ("!", "Alertas", alertas, "Con advertencias", COLORES["amarillo_suave"], COLORES["amarillo"]),
            ("×", "Errores", errores, "Requieren revisión", COLORES["rojo_suave"], COLORES["rojo"]),
        ]
        for indice, dato in enumerate(datos):
            self._tarjeta_resumen(self.resumen, *dato).grid(row=0, column=indice, sticky="nsew", padx=6, pady=4)

        if not filtrados:
            self._mostrar_sin_ejecuciones()
            return
        for registro in filtrados:
            self._crear_tarjeta(registro).pack(fill="x", pady=6)

    def _tarjeta_resumen(self, parent, icono, titulo, valor, detalle, fondo, color):
        card = ctk.CTkFrame(parent, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
        ctk.CTkLabel(card, text=icono, width=44, height=44, corner_radius=9, fg_color=fondo, text_color=color, font=(FUENTE, 18, "bold")).pack(side="left", padx=(13, 9), pady=12)
        texto = ctk.CTkFrame(card, fg_color="transparent")
        texto.pack(side="left", fill="both", expand=True, pady=9)
        ctk.CTkLabel(texto, text=titulo, text_color=COLORES["texto_secundario"], font=(FUENTE, 10)).pack(anchor="w")
        ctk.CTkLabel(texto, text=str(valor), text_color=COLORES["texto"], font=(FUENTE, 20, "bold")).pack(anchor="w")
        ctk.CTkLabel(texto, text=detalle, text_color=COLORES["texto_secundario"], font=(FUENTE, 9)).pack(anchor="w")
        return card

    def _mostrar_sin_ejecuciones(self):
        panel = ctk.CTkFrame(self.lista, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
        panel.pack(fill="x", pady=8)
        ctk.CTkLabel(panel, text="No hay ejecuciones para mostrar", text_color=COLORES["texto"], font=(FUENTE, 16, "bold")).pack(anchor="w", padx=20, pady=(20, 4))
        ctk.CTkLabel(panel, text="Las próximas ejecuciones realizadas desde AP aparecerán automáticamente aquí.", text_color=COLORES["texto_secundario"], font=(FUENTE, 12)).pack(anchor="w", padx=20, pady=(0, 20))

    def _crear_tarjeta(self, registro):
        tarjeta = ctk.CTkFrame(self.lista, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
        estado = str(registro.get("estado", ""))
        if registro.get("exitoso"):
            color_estado, fondo_estado = COLORES["verde"], COLORES["verde_suave"]
        elif estado == "ERROR":
            color_estado, fondo_estado = COLORES["rojo"], COLORES["rojo_suave"]
        else:
            color_estado, fondo_estado = COLORES["amarillo"], COLORES["amarillo_suave"]

        cuerpo = ctk.CTkFrame(tarjeta, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=18, pady=14)
        superior = ctk.CTkFrame(cuerpo, fg_color="transparent")
        superior.pack(fill="x")
        ctk.CTkLabel(superior, text=registro.get("proceso_nombre", "Proceso"), text_color=COLORES["texto"], font=(FUENTE, 15, "bold")).pack(side="left")
        ctk.CTkLabel(superior, text=estado, fg_color=fondo_estado, corner_radius=8, text_color=color_estado, font=(FUENTE, 10, "bold"), padx=9, pady=3).pack(side="right")

        inicio = str(registro.get("inicio", "")).replace("T", " ")
        duracion = self._formatear_duracion(registro.get("duracion_segundos"))
        detalle = f"{inicio}   •   Usuario: {registro.get('usuario', '')}   •   Duración: {duracion}"
        ctk.CTkLabel(cuerpo, text=detalle, text_color=COLORES["texto_secundario"], font=(FUENTE, 12)).pack(anchor="w", pady=(7, 3))
        mensaje = registro.get("mensaje", "")
        if mensaje:
            ctk.CTkLabel(cuerpo, text=mensaje, text_color=COLORES["texto_secundario"], wraplength=800, justify="left", font=(FUENTE, 12)).pack(anchor="w")

        acciones = ctk.CTkFrame(cuerpo, fg_color="transparent")
        acciones.pack(fill="x", pady=(10, 0))
        archivos = registro.get("archivos_generados", []) or []
        if archivos:
            primer_archivo = archivos[0]

            ctk.CTkButton(acciones, text="Abrir archivo", fg_color=COLORES["primario"], text_color="#111111", hover_color=COLORES["primario_hover"], font=(FUENTE, 11, "bold"), corner_radius=7, command=lambda ruta=primer_archivo: self._abrir_archivo(ruta)).pack(side="left")
            ctk.CTkButton(acciones, text="Abrir carpeta", fg_color=COLORES["panel_suave"], text_color=COLORES["texto"], font=(FUENTE, 11), corner_radius=7, border_width=1, border_color=COLORES["borde"], hover_color=COLORES["borde"], command=lambda ruta=primer_archivo: self._abrir_carpeta(ruta)).pack(side="left", padx=8)
        ctk.CTkButton(acciones, text="Detalles", fg_color=COLORES["panel_suave"], text_color=COLORES["texto"], font=(FUENTE, 11), corner_radius=7, border_width=1, border_color=COLORES["borde"], hover_color=COLORES["borde"], command=lambda dato=registro: self._mostrar_detalles(dato)).pack(side="right")

        return tarjeta

    @staticmethod
    def _formatear_duracion(segundos):
        if segundos is None:
            return "En curso"
        segundos = int(segundos)
        return f"{segundos // 3600:02d}:{(segundos % 3600) // 60:02d}:{segundos % 60:02d}"

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
        if advertencias:
            lineas.append("\nAdvertencias:\n- " + "\n- ".join(map(str, advertencias)))
        if errores:
            lineas.append("\nErrores:\n- " + "\n- ".join(map(str, errores)))
        if archivos:
            lineas.append("\nArchivos generados:\n- " + "\n- ".join(map(str, archivos)))
        messagebox.showinfo("Detalle de ejecución", "\n".join(lineas))
