import getpass
import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from interfaz.estilos import COLORES, FUENTE


class PaginaMonitoreo(tk.Frame):
    def __init__(self, parent, historial):
        super().__init__(parent, bg=COLORES["fondo"])
        self.historial = historial
        self.modo = tk.StringVar(value="todas")
        self.filtro_proceso = tk.StringVar(value="Todos")
        self.filtro_estado = tk.StringVar(value="Todos")
        self._construir_interfaz()
        self.actualizar()

    def _construir_interfaz(self):
        cabecera = tk.Frame(self, bg=COLORES["fondo"])
        cabecera.pack(fill="x", padx=28, pady=(26, 14))

        tk.Label(
            cabecera,
            text="Monitoreo",
            bg=COLORES["fondo"],
            fg=COLORES["texto"],
            font=(FUENTE, 22, "bold"),
        ).pack(anchor="w")

        tk.Label(
            cabecera,
            text="Historial de ejecuciones y resultados generados.",
            bg=COLORES["fondo"],
            fg=COLORES["texto_secundario"],
            font=(FUENTE, 10),
        ).pack(anchor="w", pady=(4, 0))

        controles = tk.Frame(self, bg=COLORES["fondo"])
        controles.pack(fill="x", padx=28, pady=(0, 12))

        ttk.Radiobutton(
            controles,
            text="Todas",
            variable=self.modo,
            value="todas",
            command=self.actualizar,
        ).pack(side="left")

        ttk.Radiobutton(
            controles,
            text="Mis ejecuciones",
            variable=self.modo,
            value="mias",
            command=self.actualizar,
        ).pack(side="left", padx=(8, 18))

        tk.Label(
            controles,
            text="Proceso",
            bg=COLORES["fondo"],
            fg=COLORES["texto_secundario"],
        ).pack(side="left")

        self.cmb_proceso = ttk.Combobox(
            controles,
            textvariable=self.filtro_proceso,
            state="readonly",
            width=22,
        )
        self.cmb_proceso.pack(side="left", padx=(6, 14))
        self.cmb_proceso.bind(
            "<<ComboboxSelected>>",
            lambda _evento: self.actualizar(),
        )

        tk.Label(
            controles,
            text="Estado",
            bg=COLORES["fondo"],
            fg=COLORES["texto_secundario"],
        ).pack(side="left")

        self.cmb_estado = ttk.Combobox(
            controles,
            textvariable=self.filtro_estado,
            state="readonly",
            width=16,
            values=["Todos", "FINALIZADO", "ERROR", "EJECUTANDO"],
        )
        self.cmb_estado.pack(side="left", padx=(6, 0))
        self.cmb_estado.bind(
            "<<ComboboxSelected>>",
            lambda _evento: self.actualizar(),
        )

        contenedor = tk.Frame(self, bg=COLORES["fondo"])
        contenedor.pack(fill="both", expand=True, padx=28, pady=(0, 22))

        self.canvas = tk.Canvas(
            contenedor,
            bg=COLORES["fondo"],
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(
            contenedor,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.lista = tk.Frame(self.canvas, bg=COLORES["fondo"])
        self.lista.bind(
            "<Configure>",
            lambda _evento: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )
        self.ventana_lista = self.canvas.create_window(
            (0, 0),
            window=self.lista,
            anchor="nw",
        )
        self.canvas.bind(
            "<Configure>",
            lambda evento: self.canvas.itemconfigure(
                self.ventana_lista,
                width=evento.width,
            ),
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def actualizar(self):
        for widget in self.lista.winfo_children():
            widget.destroy()

        usuario = getpass.getuser() if self.modo.get() == "mias" else None
        registros = self.historial.listar(solo_usuario=usuario)

        procesos = ["Todos"] + sorted(
            {r.get("proceso_nombre", "Proceso") for r in registros}
        )
        self.cmb_proceso.configure(values=procesos)
        if self.filtro_proceso.get() not in procesos:
            self.filtro_proceso.set("Todos")

        proceso = self.filtro_proceso.get()
        estado = self.filtro_estado.get()
        filtrados = [
            r
            for r in registros
            if (proceso == "Todos" or r.get("proceso_nombre") == proceso)
            and (estado == "Todos" or r.get("estado") == estado)
        ]

        if not filtrados:
            self._mostrar_sin_ejecuciones()
            return

        for registro in filtrados:
            self._crear_tarjeta(registro).pack(fill="x", pady=5)

    def _mostrar_sin_ejecuciones(self):
        panel = tk.Frame(
            self.lista,
            bg=COLORES["panel"],
            highlightbackground=COLORES["borde"],
            highlightthickness=1,
        )
        panel.pack(fill="x", pady=8)
        tk.Label(
            panel,
            text="No hay ejecuciones para mostrar",
            bg=COLORES["panel"],
            fg=COLORES["texto"],
            font=(FUENTE, 11, "bold"),
        ).pack(anchor="w", padx=18, pady=(18, 4))
        tk.Label(
            panel,
            text="Las próximas ejecuciones realizadas desde AP aparecerán automáticamente aquí.",
            bg=COLORES["panel"],
            fg=COLORES["texto_secundario"],
            font=(FUENTE, 9),
        ).pack(anchor="w", padx=18, pady=(0, 18))

    def _crear_tarjeta(self, registro):
        tarjeta = tk.Frame(
            self.lista,
            bg=COLORES["panel"],
            highlightbackground=COLORES["borde"],
            highlightthickness=1,
        )

        estado = str(registro.get("estado", ""))
        if registro.get("exitoso"):
            color_estado = COLORES["verde"]
        elif estado == "ERROR":
            color_estado = COLORES["rojo"]
        else:
            color_estado = COLORES["amarillo"]

        tk.Frame(tarjeta, width=4, bg=color_estado).pack(side="left", fill="y")

        cuerpo = tk.Frame(tarjeta, bg=COLORES["panel"])
        cuerpo.pack(fill="both", expand=True, padx=14, pady=12)

        superior = tk.Frame(cuerpo, bg=COLORES["panel"])
        superior.pack(fill="x")

        tk.Label(
            superior,
            text=registro.get("proceso_nombre", "Proceso"),
            bg=COLORES["panel"],
            fg=COLORES["texto"],
            font=(FUENTE, 11, "bold"),
        ).pack(side="left")

        tk.Label(
            superior,
            text=estado,
            bg=COLORES["panel"],
            fg=color_estado,
            font=(FUENTE, 9, "bold"),
        ).pack(side="right")

        inicio = str(registro.get("inicio", "")).replace("T", " ")
        duracion = self._formatear_duracion(registro.get("duracion_segundos"))
        detalle = (
            f"{inicio}   •   Usuario: {registro.get('usuario', '')}"
            f"   •   Duración: {duracion}"
        )
        tk.Label(
            cuerpo,
            text=detalle,
            bg=COLORES["panel"],
            fg=COLORES["texto_secundario"],
            font=(FUENTE, 9),
        ).pack(anchor="w", pady=(5, 4))

        mensaje = registro.get("mensaje", "")
        if mensaje:
            tk.Label(
                cuerpo,
                text=mensaje,
                bg=COLORES["panel"],
                fg=COLORES["texto_secundario"],
                wraplength=760,
                justify="left",
                font=(FUENTE, 9),
            ).pack(anchor="w")

        acciones = tk.Frame(cuerpo, bg=COLORES["panel"])
        acciones.pack(fill="x", pady=(8, 0))

        archivos = registro.get("archivos_generados", []) or []
        if archivos:
            primer_archivo = archivos[0]

            tk.Button(
                acciones,
                text="Abrir archivo",
                relief="flat",
                bd=0,
                bg=COLORES["primario"],
                fg="white",
                activebackground=COLORES["primario_hover"],
                activeforeground="white",
                font=(FUENTE, 9, "bold"),
                padx=10,
                pady=6,
                cursor="hand2",
                command=lambda ruta=primer_archivo: self._abrir_archivo(ruta),
            ).pack(side="left")

            tk.Button(
                acciones,
                text="Abrir carpeta",
                relief="flat",
                bd=0,
                bg=COLORES["panel_suave"],
                fg=COLORES["texto"],
                font=(FUENTE, 9),
                padx=10,
                pady=6,
                cursor="hand2",
                command=lambda ruta=primer_archivo: self._abrir_carpeta(ruta),
            ).pack(side="left", padx=6)

        tk.Button(
            acciones,
            text="Detalles",
            relief="flat",
            bd=0,
            bg=COLORES["panel_suave"],
            fg=COLORES["texto"],
            font=(FUENTE, 9),
            padx=10,
            pady=6,
            cursor="hand2",
            command=lambda dato=registro: self._mostrar_detalles(dato),
        ).pack(side="right")

        return tarjeta

    @staticmethod
    def _formatear_duracion(segundos):
        if segundos is None:
            return "En curso"
        segundos = int(segundos)
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos_restantes = segundos % 60
        return f"{horas:02d}:{minutos:02d}:{segundos_restantes:02d}"

    def _abrir_archivo(self, ruta):
        archivo = Path(ruta)
        if not archivo.exists():
            messagebox.showwarning(
                "Archivo",
                f"El archivo ya no existe:\n\n{archivo}",
            )
            return
        self._abrir(archivo)

    def _abrir_carpeta(self, ruta):
        ruta = Path(ruta)
        carpeta = ruta if ruta.is_dir() else ruta.parent
        if not carpeta.exists():
            messagebox.showwarning(
                "Carpeta",
                f"La carpeta ya no existe:\n\n{carpeta}",
            )
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

        messagebox.showinfo(
            "Detalle de ejecución",
            "\n".join(lineas),
        )
