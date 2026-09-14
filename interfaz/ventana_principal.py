import os
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict
from nucleo.ejecutor import ejecutar_proyecto
from interfaz.widgets.sidebar import Sidebar
from interfaz.paginas.dashboard import DashboardPage
from interfaz.paginas.procesos import PaginaProcesos
from interfaz.paginas.monitoreo import PaginaMonitoreo
from interfaz.paginas.configuracion import (
    PaginaConfiguracion
)


COLORES = {
    "fondo": "#F4F7FB",
    "panel": "#FFFFFF",
    "azul": "#0F5CC0",
    "azul_oscuro": "#17365D",
    "texto": "#1E293B",
    "texto_secundario": "#64748B",
    "borde": "#DCE3EC",
    "verde": "#15803D",
    "amarillo": "#B45309",
    "rojo": "#B91C1C",
    "violeta": "#6D28D9",
}

MESES = [
    ("Enero", 1), ("Febrero", 2), ("Marzo", 3), ("Abril", 4),
    ("Mayo", 5), ("Junio", 6), ("Julio", 7), ("Agosto", 8),
    ("Septiembre", 9), ("Octubre", 10), ("Noviembre", 11),
    ("Diciembre", 12),
]


class VentanaPrincipal(tk.Tk):
    def __init__(self, registro, configuracion):
        super().__init__()
        self.registro = registro
        self.configuracion = configuracion
        self.proyecto_actual = None
        self.campos: Dict[str, Dict[str, Any]] = {}
        self.en_ejecucion = False
        self.ultimo_resultado = None

        self.title("Plataforma de Procesos")
        self.geometry("1180x760")
        self.minsize(1020, 680)
        self.configure(bg=COLORES["fondo"])
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

        self._configurar_estilos()
        self._construir_encabezado()
        self._construir_contenido()
        self._construir_pie()
        self._mostrar_inicio()

    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure("TFrame", background=COLORES["fondo"])
        estilo.configure("Panel.TFrame", background=COLORES["panel"])
        estilo.configure(
            "Titulo.TLabel",
            background=COLORES["fondo"],
            foreground=COLORES["azul_oscuro"],
            font=("Segoe UI", 22, "bold"),
        )
        estilo.configure(
            "Subtitulo.TLabel",
            background=COLORES["fondo"],
            foreground=COLORES["texto_secundario"],
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "PanelTitulo.TLabel",
            background=COLORES["panel"],
            foreground=COLORES["texto"],
            font=("Segoe UI", 15, "bold"),
        )
        estilo.configure(
            "TextoPanel.TLabel",
            background=COLORES["panel"],
            foreground=COLORES["texto_secundario"],
            font=("Segoe UI", 10),
        )
        estilo.configure("TButton", font=("Segoe UI", 10), padding=(12, 8))
        estilo.configure(
            "Primary.TButton",
            background=COLORES["azul"],
            foreground="white",
            font=("Segoe UI", 10, "bold"),
        )
        estilo.map(
            "Primary.TButton",
            background=[("active", "#0B4DA3"), ("disabled", "#9FB8D8")],
        )
        estilo.configure(
            "Project.TButton",
            background=COLORES["panel"],
            foreground=COLORES["texto"],
            anchor="w",
            font=("Segoe UI", 11, "bold"),
            padding=(16, 14),
        )
        estilo.map("Project.TButton", background=[("active", "#EAF2FF")])
        estilo.configure("Horizontal.TProgressbar", troughcolor="#E2E8F0", background=COLORES["azul"])

    def _construir_encabezado(self):
        cabecera = ttk.Frame(self)
        cabecera.pack(fill="x", padx=28, pady=(24, 14))

        izquierda = ttk.Frame(cabecera)
        izquierda.pack(side="left", fill="x", expand=True)
        ttk.Label(izquierda, text="Plataforma de Procesos", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            izquierda,
            text="Automatizaciones modulares, trazables y protegidas",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        version = self.configuracion.get("version", "0.2.0")
        ttk.Label(
            cabecera,
            text=f"Versión {version}",
            style="Subtitulo.TLabel",
        ).pack(side="right", anchor="n", pady=6)

    def _construir_contenido(self):
        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True, padx=28, pady=(0, 14))

        self.panel_proyectos = tk.Frame(
            cuerpo,
            bg=COLORES["panel"],
            highlightbackground=COLORES["borde"],
            highlightthickness=1,
            width=290,
        )
        self.panel_proyectos.pack(side="left", fill="y")
        self.panel_proyectos.pack_propagate(False)

        tk.Label(
            self.panel_proyectos,
            text="PROYECTOS",
            bg=COLORES["panel"],
            fg=COLORES["texto_secundario"],
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=18, pady=(20, 10))

        for metadatos in self.registro.listar():
            boton = ttk.Button(
                self.panel_proyectos,
                text=f"  {metadatos['nombre']}\n  {metadatos['estado']}",
                style="Project.TButton",
                command=lambda identificador=metadatos["id"]: self._seleccionar_proyecto(identificador),
            )
            boton.pack(fill="x", padx=12, pady=5)

        separador = tk.Frame(self.panel_proyectos, height=1, bg=COLORES["borde"])
        separador.pack(fill="x", padx=18, pady=18)

        tk.Label(
            self.panel_proyectos,
            text="Los motores permanecen en sus\nproyectos originales.",
            justify="left",
            bg=COLORES["panel"],
            fg=COLORES["texto_secundario"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=18)

        self.panel_principal = tk.Frame(
            cuerpo,
            bg=COLORES["panel"],
            highlightbackground=COLORES["borde"],
            highlightthickness=1,
        )
        self.panel_principal.pack(side="left", fill="both", expand=True, padx=(16, 0))

    def _construir_pie(self):
        pie = ttk.Frame(self)
        pie.pack(fill="x", padx=28, pady=(0, 18))
        self.estado_global = ttk.Label(
            pie,
            text="Listo",
            style="Subtitulo.TLabel",
        )
        self.estado_global.pack(side="left")
        ttk.Label(
            pie,
            text="No se publican resultados corporativos desde esta fase.",
            style="Subtitulo.TLabel",
        ).pack(side="right")

    def _limpiar_panel(self):
        for elemento in self.panel_principal.winfo_children():
            elemento.destroy()
        self.campos = {}
    def _mostrar_inicio(self):

        self._limpiar_panel()

        dashboard = DashboardPage(
            self.panel_principal,
            self.registro
        )

        dashboard.pack(
            fill="both",
            expand=True
        )

    def _tarjeta_resumen(self, padre, titulo, descripcion, color):

        tarjeta = tk.Frame(
            padre,
            bg="#F8FAFC",
            highlightbackground=COLORES["borde"],
            highlightthickness=1,
        )

        barra = tk.Frame(
            tarjeta,
            bg=color,
            width=6
        )

        barra.pack(
            side="left",
            fill="y"
        )

        contenido = tk.Frame(
            tarjeta,
            bg="#F8FAFC"
        )

        contenido.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=16
        )

        tk.Label(
            contenido,
            text=titulo,
            bg="#F8FAFC",
            fg=COLORES["texto"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w")

        tk.Label(
            contenido,
            text=descripcion,
            wraplength=680,
            justify="left",
            bg="#F8FAFC",
            fg=COLORES["texto_secundario"],
            font=("Segoe UI", 9),
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        return tarjeta
   
    def _seleccionar_proyecto(self, identificador):
        if self.en_ejecucion:
            messagebox.showwarning("Proceso en ejecución", "Espere a que termine la ejecución actual.")
            return

        self.proyecto_actual = self.registro.obtener(identificador)
        self.ultimo_resultado = None
        metadatos = self.proyecto_actual.obtener_metadatos()
        disponibilidad = self.proyecto_actual.validar_disponibilidad()
        self._limpiar_panel()

        cabecera = tk.Frame(self.panel_principal, bg=COLORES["panel"])
        cabecera.pack(fill="x", padx=30, pady=(26, 12))
        tk.Label(
            cabecera,
            text=metadatos["nombre"],
            bg=COLORES["panel"],
            fg=COLORES["azul_oscuro"],
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w")
        tk.Label(
            cabecera,
            text=metadatos["descripcion"],
            bg=COLORES["panel"],
            fg=COLORES["texto_secundario"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        color_disponibilidad = COLORES["verde"] if disponibilidad["disponible"] else COLORES["rojo"]
        tk.Label(
            cabecera,
            text=disponibilidad["mensaje"],
            bg=COLORES["panel"],
            fg=color_disponibilidad,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(8, 0))

        formulario = tk.Frame(self.panel_principal, bg=COLORES["panel"])
        formulario.pack(fill="x", padx=30, pady=10)

        for fila, campo in enumerate(self.proyecto_actual.obtener_campos_configuracion()):
            self._crear_campo(formulario, fila, campo)

        if identificador == "comisiones":
            self._crear_aviso(
                "Las diferencias de conciliación son informativas y no bloquean la generación del informe.",
                "#FFF7ED",
                COLORES["amarillo"],
            )
        elif identificador == "inversiones":
            self._crear_aviso(
                "Inversiones permanece en modo local protegido. La publicación corporativa está bloqueada.",
                "#F5F3FF",
                COLORES["violeta"],
            )

        acciones = tk.Frame(self.panel_principal, bg=COLORES["panel"])
        acciones.pack(fill="x", padx=30, pady=(12, 8))
        ttk.Button(acciones, text="Validar parámetros", command=self._validar).pack(side="left")
        self.boton_ejecutar = ttk.Button(
            acciones,
            text="Ejecutar módulo",
            style="Primary.TButton",
            command=self._ejecutar,
        )
        self.boton_ejecutar.pack(side="left", padx=8)
        ttk.Button(acciones, text="Abrir carpeta local", command=self._abrir_carpeta).pack(side="left")
        self.boton_abrir_archivo = ttk.Button(
            acciones,
            text="Abrir informe",
            command=self._abrir_ultimo_archivo,
            state="disabled",
        )
        self.boton_abrir_archivo.pack(side="left", padx=8)

        self.progreso = ttk.Progressbar(
            self.panel_principal,
            mode="determinate",
            maximum=100,
        )
        self.progreso.pack(fill="x", padx=30, pady=(10, 4))

        self.etiqueta_progreso = tk.Label(
            self.panel_principal,
            text="Esperando validación...",
            anchor="w",
            bg=COLORES["panel"],
            fg=COLORES["texto_secundario"],
            font=("Segoe UI", 9),
        )
        self.etiqueta_progreso.pack(fill="x", padx=30)

        self.consola = tk.Text(
            self.panel_principal,
            height=9,
            bg="#0F172A",
            fg="#D7E3F4",
            insertbackground="white",
            relief="flat",
            font=("Consolas", 9),
            padx=12,
            pady=10,
            state="disabled",
        )
        self.consola.pack(fill="both", expand=True, padx=30, pady=(12, 8))
        self.panel_resultado = tk.Frame(
            self.panel_principal,
            bg="#F8FAFC",
            highlightbackground=COLORES["borde"],
            highlightthickness=1,
        )
        self.panel_resultado.pack(fill="x", padx=30, pady=(0, 24))
        tk.Label(
            self.panel_resultado,
            text="El resumen de la última ejecución aparecerá aquí.",
            bg="#F8FAFC",
            fg=COLORES["texto_secundario"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=14, pady=12)
        self._escribir_consola("Módulo cargado. No se ha ejecutado ningún motor.")

    def _crear_campo(self, padre, fila, campo):
        tk.Label(
            padre,
            text=campo["etiqueta"],
            bg=COLORES["panel"],
            fg=COLORES["texto"],
            font=("Segoe UI", 10),
        ).grid(row=fila, column=0, sticky="w", padx=(0, 16), pady=7)

        tipo = campo["tipo"]
        variable = tk.StringVar()
        control = None

        if campo["id"] == "anio":
            variable.set("2026")
        elif campo["id"] == "mes":
            variable.set("7")
        elif campo["id"] == "periodo":
            variable.set("2025-12")

        if tipo == "mes":
            variable_visual = tk.StringVar(value="Julio")
            control = ttk.Combobox(
                padre,
                textvariable=variable_visual,
                values=[nombre for nombre, _ in MESES],
                state="readonly",
                width=37,
            )
            control.grid(row=fila, column=1, sticky="ew", pady=7)
            self.campos[campo["id"]] = {
                "variable": variable,
                "visual": variable_visual,
                "tipo": tipo,
            }
            return

        if tipo == "archivo_excel":
            control = ttk.Entry(padre, textvariable=variable, width=42)
            control.grid(row=fila, column=1, sticky="ew", pady=7)
            ttk.Button(
                padre,
                text="Seleccionar archivo",
                command=lambda var=variable: self._seleccionar_archivo_excel(var),
            ).grid(row=fila, column=2, padx=(8, 0), pady=7)
            padre.grid_columnconfigure(1, weight=1)
            self.campos[campo["id"]] = {"variable": variable, "tipo": tipo}
            return

        if tipo == "booleano":
            variable.set("0")
            control = ttk.Checkbutton(
                padre,
                variable=variable,
                onvalue="1",
                offvalue="0",
                state="disabled" if campo.get("bloqueado") else "normal",
            )
            control.grid(row=fila, column=1, sticky="w", pady=7)
        else:
            control = ttk.Entry(padre, textvariable=variable, width=42)
            control.grid(row=fila, column=1, sticky="ew", pady=7)

        if tipo == "carpeta":
            ttk.Button(
                padre,
                text="Seleccionar",
                command=lambda var=variable: self._seleccionar_carpeta(var),
            ).grid(row=fila, column=2, padx=(8, 0), pady=7)

        padre.grid_columnconfigure(1, weight=1)
        self.campos[campo["id"]] = {"variable": variable, "tipo": tipo}

    def _crear_aviso(self, texto, fondo, color):
        aviso = tk.Frame(self.panel_principal, bg=fondo)
        aviso.pack(fill="x", padx=30, pady=(8, 4))
        tk.Label(
            aviso,
            text=texto,
            wraplength=700,
            justify="left",
            bg=fondo,
            fg=color,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=14, pady=12)

    def _seleccionar_carpeta(self, variable):
        ruta = filedialog.askdirectory(title="Seleccione una carpeta local")
        if ruta:
            variable.set(ruta)

    def _seleccionar_archivo_excel(self, variable):
        ruta = filedialog.askopenfilename(
            title="Seleccione el archivo de cierre mensual",
            filetypes=[
                ("Archivos Excel", "*.xlsx *.xlsm *.xlsb"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if ruta:
            variable.set(ruta)

    def _recoger_parametros(self):
        parametros = {}
        for identificador, campo in self.campos.items():
            if campo["tipo"] == "mes":
                nombre = campo["visual"].get()
                parametros[identificador] = dict(MESES)[nombre]
            elif campo["tipo"] == "booleano":
                parametros[identificador] = campo["variable"].get() == "1"
            else:
                parametros[identificador] = campo["variable"].get().strip()
        return parametros

    def _validar(self):
        if self.proyecto_actual is None:
            return False
        errores = self.proyecto_actual.validar_parametros(self._recoger_parametros())
        if errores:
            self._escribir_consola("VALIDACIÓN CON ERRORES:")
            for error in errores:
                self._escribir_consola(f"  - {error}")
            messagebox.showwarning("Validación", "Revise los parámetros indicados en el registro.")
            return False
        self._escribir_consola("Parámetros válidos para la fase actual.")
        self.etiqueta_progreso.config(text="Parámetros válidos.")
        return True

    def _ejecutar(self):
        if self.en_ejecucion or not self._validar():
            return
        self.en_ejecucion = True
        self.boton_ejecutar.config(state="disabled")
        self.progreso["value"] = 0
        parametros = self._recoger_parametros()
        hilo = threading.Thread(
            target=self._ejecucion_en_segundo_plano,
            args=(parametros,),
            daemon=True,
        )
        hilo.start()

    def _ejecucion_en_segundo_plano(self, parametros):
        try:
            resultado = ejecutar_proyecto(
                self.proyecto_actual,
                parametros,
                self._reportar_evento_desde_hilo,
            )
            self.after(0, lambda: self._finalizar_ejecucion(resultado))
        except Exception as error:
            resultado = {
                "exitoso": False,
                "estado": "ERROR",
                "mensaje": str(error),
                "errores": [str(error)],
            }
            self.after(0, lambda: self._finalizar_ejecucion(resultado))

    def _reportar_evento_desde_hilo(self, estado, mensaje, porcentaje):
        self.after(0, lambda: self._aplicar_evento(estado, mensaje, porcentaje))

    def _aplicar_evento(self, estado, mensaje, porcentaje):
        self.progreso["value"] = porcentaje
        self.etiqueta_progreso.config(text=f"{estado}: {mensaje}")
        self._escribir_consola(f"[{estado}] {mensaje}")

    def _finalizar_ejecucion(self, resultado):
        self.ultimo_resultado = resultado
        self.en_ejecucion = False
        self.boton_ejecutar.config(state="normal")
        self._escribir_consola(f"Estado final: {resultado.get('estado')}")
        self._escribir_consola(resultado.get("mensaje", ""))
        for advertencia in resultado.get("advertencias", []):
            self._escribir_consola(f"[ADVERTENCIA] {advertencia}")
        for error in resultado.get("errores", []):
            self._escribir_consola(f"[ERROR] {error}")
        self.etiqueta_progreso.config(text=resultado.get("mensaje", "Proceso finalizado."))
        self._mostrar_resumen_resultado(resultado)
        archivos = resultado.get("archivos_generados", [])
        if archivos and hasattr(self, "boton_abrir_archivo"):
            self.boton_abrir_archivo.config(state="normal")
        if resultado.get("exitoso"):
            self.progreso["value"] = 100
            messagebox.showinfo("Ejecución", resultado.get("mensaje", "Proceso finalizado."))
        else:
            messagebox.showwarning("Ejecución", resultado.get("mensaje", "Proceso no ejecutado."))

    def _escribir_consola(self, texto):
        if not hasattr(self, "consola"):
            return
        self.consola.config(state="normal")
        self.consola.insert("end", texto + "\n")
        self.consola.see("end")
        self.consola.config(state="disabled")

    def _abrir_carpeta(self):
        campo = self.campos.get("carpeta_salida")
        if not campo:
            return
        ruta = campo["variable"].get().strip()
        if not ruta:
            messagebox.showwarning("Carpeta", "Seleccione primero una carpeta local.")
            return
        carpeta = Path(ruta)
        if not carpeta.exists():
            carpeta.mkdir(parents=True, exist_ok=True)
        try:
            if os.name == "nt":
                os.startfile(str(carpeta))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(carpeta)])
            else:
                subprocess.Popen(["xdg-open", str(carpeta)])
        except Exception as error:
            messagebox.showerror("Carpeta", str(error))

    def _mostrar_resumen_resultado(self, resultado):
        if not hasattr(self, "panel_resultado"):
            return
        for elemento in self.panel_resultado.winfo_children():
            elemento.destroy()

        estado = str(resultado.get("estado", "SIN ESTADO"))
        color = COLORES["verde"] if resultado.get("exitoso") else COLORES["amarillo"]
        if estado == "ERROR":
            color = COLORES["rojo"]

        cabecera = tk.Frame(self.panel_resultado, bg="#F8FAFC")
        cabecera.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(
            cabecera, text="RESUMEN DE LA EJECUCIÓN", bg="#F8FAFC",
            fg=COLORES["texto_secundario"], font=("Segoe UI", 9, "bold"),
        ).pack(side="left")
        tk.Label(
            cabecera, text=estado, bg="#F8FAFC", fg=color,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right")

        metricas = resultado.get("metricas", {}) or {}
        filas = [
            ("Periodo", metricas.get("periodo")),
            ("Estado del motor", metricas.get("estado_motor")),
            ("Registros contables", metricas.get("registros_contables")),
            ("Facturas pendientes", metricas.get("facturas_pendientes")),
            ("Llaves procesadas", metricas.get("llaves")),
            ("Negocios consolidados", metricas.get("negocios")),
        ]
        disponibles = [(nombre, valor) for nombre, valor in filas if valor is not None]
        if disponibles:
            rejilla = tk.Frame(self.panel_resultado, bg="#F8FAFC")
            rejilla.pack(fill="x", padx=10, pady=(2, 8))
            for indice, (nombre, valor) in enumerate(disponibles):
                tarjeta = tk.Frame(
                    rejilla, bg="white", highlightbackground=COLORES["borde"],
                    highlightthickness=1,
                )
                tarjeta.grid(row=indice // 3, column=indice % 3, sticky="nsew", padx=4, pady=4)
                tk.Label(
                    tarjeta, text=nombre, bg="white", fg=COLORES["texto_secundario"],
                    font=("Segoe UI", 8),
                ).pack(anchor="w", padx=10, pady=(8, 2))
                tk.Label(
                    tarjeta, text=str(valor), bg="white", fg=COLORES["texto"],
                    font=("Segoe UI", 11, "bold"),
                ).pack(anchor="w", padx=10, pady=(0, 8))
            for columna in range(3):
                rejilla.grid_columnconfigure(columna, weight=1)

        archivos = resultado.get("archivos_generados", [])
        if archivos:
            tk.Label(
                self.panel_resultado, text=f"Informe: {archivos[0]}",
                wraplength=760, justify="left", bg="#F8FAFC",
                fg=COLORES["azul"], font=("Segoe UI", 8),
            ).pack(anchor="w", padx=14, pady=(0, 12))

    def _abrir_ultimo_archivo(self):
        if not self.ultimo_resultado:
            return
        archivos = self.ultimo_resultado.get("archivos_generados", [])
        if not archivos:
            messagebox.showwarning("Informe", "No hay un informe disponible.")
            return
        ruta = Path(archivos[0])
        if not ruta.exists():
            messagebox.showerror("Informe", f"No existe el archivo: {ruta}")
            return
        try:
            if os.name == "nt":
                os.startfile(str(ruta))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(ruta)])
            else:
                subprocess.Popen(["xdg-open", str(ruta)])
        except Exception as error:
            messagebox.showerror("Informe", str(error))

    def _cerrar(self):
        if self.en_ejecucion:
            if not messagebox.askyesno(
                "Cerrar",
                "Hay un proceso en ejecución. ¿Desea cerrar de todas formas?",
            ):
                return
        self.destroy()
