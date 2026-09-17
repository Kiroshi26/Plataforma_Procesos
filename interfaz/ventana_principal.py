import os
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict
from nucleo.ejecutor import ejecutar_proyecto
from nucleo.historial_ejecuciones import HistorialEjecuciones
from nucleo.gestor_preferencias import GestorPreferencias
from interfaz.widgets.sidebar import Sidebar
from interfaz.paginas.dashboard import DashboardPage
from interfaz.paginas.procesos import PaginaProcesos
from interfaz.paginas.monitoreo import PaginaMonitoreo
from interfaz.paginas.configuracion import PaginaConfiguracion
from interfaz.estilos import COLORES, FUENTE, aplicar_tema


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
        self.preferencias = GestorPreferencias()
        aplicar_tema(self.preferencias.obtener("tema", "claro"))
        self.proyecto_actual = None
        self.campos: Dict[str, Dict[str, Any]] = {}
        self.en_ejecucion = False
        self.ultimo_resultado = None
        self.pagina_actual = "inicio"
        self.historial = HistorialEjecuciones(
            self.preferencias.obtener("historial", r"C:\Proyectos\pruebas\Historial_AP")
        )
        self.ejecucion_historial_actual = None

        self.title("Aplicativo de Procesos")
        self.geometry(
            self.preferencias.obtener("geometria", "1280x800")
            if self.preferencias.obtener("recordar_ventana", True)
            else "1280x800"
        )
        self.minsize(980, 640)
        self.configure(bg=COLORES["fondo"])
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

        self._configurar_estilos()
        self._construir_encabezado()
        self._construir_contenido()
        self._construir_pie()
        if (
            self.preferencias.obtener("recordar_sidebar", True)
            and self.preferencias.obtener("sidebar_colapsada", False)
            and not self.sidebar.colapsada
        ):
            self.sidebar.alternar()
        if (
            self.preferencias.obtener("recordar_ventana", True)
            and self.preferencias.obtener("estado_ventana") == "zoomed"
        ):
            try:
                self.state("zoomed")
            except tk.TclError:
                pass
        self.sidebar.seleccionar("inicio", notificar=False)
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
            foreground=COLORES["texto"],
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
        estilo.configure(
            "TButton",
            background=COLORES["panel_suave"],
            foreground=COLORES["texto"],
            font=("Segoe UI", 10),
            padding=(12, 8),
        )
        estilo.map(
            "TButton",
            background=[("active", COLORES["primario_suave"])],
            foreground=[("active", COLORES["primario"])],
        )
        estilo.configure(
            "TEntry",
            fieldbackground=COLORES["panel"],
            foreground=COLORES["texto"],
            insertcolor=COLORES["texto"],
        )
        estilo.configure(
            "TCombobox",
            fieldbackground=COLORES["panel"],
            background=COLORES["panel"],
            foreground=COLORES["texto"],
            arrowcolor=COLORES["texto_secundario"],
        )
        estilo.map(
            "TCombobox",
            fieldbackground=[("readonly", COLORES["panel"])],
            foreground=[("readonly", COLORES["texto"])],
            selectbackground=[("readonly", COLORES["panel"])],
            selectforeground=[("readonly", COLORES["texto"])],
        )
        estilo.configure(
            "TCheckbutton",
            background=COLORES["panel"],
            foreground=COLORES["texto"],
        )
        estilo.map(
            "TCheckbutton",
            background=[("active", COLORES["panel"])],
            foreground=[("active", COLORES["primario"])],
        )
        estilo.configure(
            "TRadiobutton",
            background=COLORES["panel"],
            foreground=COLORES["texto"],
        )
        estilo.map(
            "TRadiobutton",
            background=[("active", COLORES["panel"])],
            foreground=[("active", COLORES["primario"])],
        )
        estilo.configure(
            "Primary.TButton",
            background=COLORES["primario"],
            foreground="white",
            font=("Segoe UI", 10, "bold"),
        )
        estilo.map(
            "Primary.TButton",
            background=[("active", COLORES["primario_hover"]), ("disabled", COLORES["texto_secundario"])],
        )
        estilo.configure(
            "Project.TButton",
            background=COLORES["panel"],
            foreground=COLORES["texto"],
            anchor="w",
            font=("Segoe UI", 11, "bold"),
            padding=(16, 14),
        )
        estilo.map("Project.TButton", background=[("active", COLORES["primario_suave"])])
        estilo.configure("Horizontal.TProgressbar", troughcolor=COLORES["borde"], background=COLORES["primario"])

    def _construir_encabezado(self):
        cabecera = ttk.Frame(self)
        cabecera.pack(fill="x", padx=20, pady=(18, 12))

        izquierda = ttk.Frame(cabecera)
        izquierda.pack(side="left", fill="x", expand=True)
        ttk.Label(izquierda, text="Aplicativo de Procesos", style="Titulo.TLabel").pack(anchor="w")
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
        cuerpo = tk.Frame(self, bg=COLORES["fondo"])
        cuerpo.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        self.sidebar = Sidebar(cuerpo, on_navegar=self._navegar)
        self.sidebar.pack(side="left", fill="y")

        self.panel_principal = tk.Frame(
            cuerpo,
            bg=COLORES["fondo"],
            highlightbackground=COLORES["borde"],
            highlightthickness=1,
        )
        self.panel_principal.pack(side="left", fill="both", expand=True, padx=(12, 0))

    def _navegar(self, pagina):
        if self.en_ejecucion and pagina != self.pagina_actual:
            if not messagebox.askyesno(
                "Proceso en ejecución",
                "Hay un proceso en ejecución. ¿Desea cambiar de vista sin detenerlo?",
            ):
                self.sidebar.seleccionar(self.pagina_actual, notificar=False)
                return

        self.pagina_actual = pagina
        self.sidebar.seleccionar(pagina, notificar=False)

        if pagina == "inicio":
            self._mostrar_inicio()
        elif pagina == "procesos":
            self._mostrar_procesos()
        elif pagina == "monitoreo":
            self._mostrar_monitoreo()
        elif pagina == "configuracion":
            self._mostrar_configuracion()

    def _mostrar_procesos(self):
        self._limpiar_panel()
        pagina = PaginaProcesos(
            self.panel_principal,
            self.registro,
            self._abrir_proyecto_desde_catalogo,
        )
        pagina.pack(fill="both", expand=True)

    def _mostrar_pagina_simple(self, clase_pagina):
        self._limpiar_panel()
        pagina = clase_pagina(self.panel_principal)
        pagina.pack(fill="both", expand=True)

    def _mostrar_monitoreo(self):
        self._limpiar_panel()
        pagina = PaginaMonitoreo(
            self.panel_principal,
            self.historial,
        )
        pagina.pack(fill="both", expand=True)

    def _mostrar_configuracion(self):
        self._limpiar_panel()
        pagina = PaginaConfiguracion(
            self.panel_principal,
            self.preferencias,
            self.configuracion.get("version", "0.4.0"),
            len(self.registro.listar()),
            on_guardar=self._aplicar_preferencias_en_ejecucion,
        )
        pagina.pack(fill="both", expand=True)

    def _aplicar_preferencias_en_ejecucion(self, datos):
        if self.en_ejecucion:
            messagebox.showwarning(
                "Configuración",
                "El tema no puede cambiar mientras hay un proceso en ejecución.",
            )
            return

        tema_anterior = COLORES.copy()
        aplicar_tema(datos.get("tema", "claro"))

        if tema_anterior != COLORES:
            self._reconstruir_interfaz("configuracion")

    def _reconstruir_interfaz(self, pagina_destino="inicio"):
        for widget in self.winfo_children():
            widget.destroy()

        self.configure(bg=COLORES["fondo"])
        self._configurar_estilos()
        self._construir_encabezado()
        self._construir_contenido()
        self._construir_pie()

        if (
            self.preferencias.obtener("recordar_sidebar", True)
            and self.preferencias.obtener("sidebar_colapsada", False)
            and not self.sidebar.colapsada
        ):
            self.sidebar.alternar()

        self.pagina_actual = pagina_destino
        self.sidebar.seleccionar(pagina_destino, notificar=False)
        if pagina_destino == "configuracion":
            self._mostrar_configuracion()
        elif pagina_destino == "monitoreo":
            self._mostrar_monitoreo()
        elif pagina_destino == "procesos":
            self._mostrar_procesos()
        else:
            self._mostrar_inicio()

    def _abrir_proyecto_desde_catalogo(self, identificador):
        self.pagina_actual = "procesos"
        self.sidebar.seleccionar("procesos", notificar=False)
        self._seleccionar_proyecto(identificador)

    def _construir_pie(self):
        pie = ttk.Frame(self)
        pie.pack(fill="x", padx=20, pady=(0, 12))
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
            self.registro,
            self._abrir_proyecto_desde_catalogo,
        )

        dashboard.pack(
            fill="both",
            expand=True
        )

    def _tarjeta_resumen(self, padre, titulo, descripcion, color):

        tarjeta = tk.Frame(
            padre,
            bg=COLORES["panel_suave"],
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
            bg=COLORES["panel_suave"]
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
            bg=COLORES["panel_suave"],
            fg=COLORES["texto"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w")

        tk.Label(
            contenido,
            text=descripcion,
            wraplength=680,
            justify="left",
            bg=COLORES["panel_suave"],
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
            fg=COLORES["texto"],
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
            bg=COLORES["consola"],
            fg=COLORES["consola_texto"],
            insertbackground="white",
            relief="flat",
            font=("Consolas", 9),
            padx=12,
            pady=10,
            state="disabled",
        )
        if self.preferencias.obtener("mostrar_consola", True):
            self.consola.pack(fill="both", expand=True, padx=30, pady=(12, 8))
        self.panel_resultado = tk.Frame(
            self.panel_principal,
            bg=COLORES["panel_suave"],
            highlightbackground=COLORES["borde"],
            highlightthickness=1,
        )
        self.panel_resultado.pack(fill="x", padx=30, pady=(0, 24))
        tk.Label(
            self.panel_resultado,
            text="El resumen de la última ejecución aparecerá aquí.",
            bg=COLORES["panel_suave"],
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

        if tipo == "password":
            control = ttk.Entry(
                padre,
                textvariable=variable,
                width=42,
                show="*",
            )
            control.grid(row=fila, column=1, sticky="ew", pady=7)
            padre.grid_columnconfigure(1, weight=1)
            self.campos[campo["id"]] = {
                "variable": variable,
                "tipo": tipo,
                "sensible": True,
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
        try:
            self.ejecucion_historial_actual = self.historial.iniciar(
                self.proyecto_actual.obtener_metadatos(),
                parametros,
            )
        except Exception as error:
            self.ejecucion_historial_actual = None
            self._escribir_consola(
                f"[ADVERTENCIA] No fue posible iniciar el historial: {error}"
            )
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
        try:
            self.historial.agregar_evento(
                self.ejecucion_historial_actual,
                estado,
                mensaje,
                porcentaje,
            )
        except Exception:
            pass

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
        try:
            self.historial.finalizar(
                self.ejecucion_historial_actual,
                resultado,
            )
        except Exception as error:
            self._escribir_consola(
                f"[ADVERTENCIA] No fue posible finalizar el historial: {error}"
            )
        finally:
            self.ejecucion_historial_actual = None
        self._mostrar_resumen_resultado(resultado)
        archivos = resultado.get("archivos_generados", [])
        if archivos and hasattr(self, "boton_abrir_archivo"):
            self.boton_abrir_archivo.config(state="normal")
        if resultado.get("exitoso"):
            self.progreso["value"] = 100
            messagebox.showinfo("Ejecución", resultado.get("mensaje", "Proceso finalizado."))
            if (
                self.preferencias.obtener("abrir_resultado_automaticamente", False)
                and archivos
            ):
                self._abrir_ultimo_archivo()
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

        cabecera = tk.Frame(self.panel_resultado, bg=COLORES["panel_suave"])
        cabecera.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(
            cabecera, text="RESUMEN DE LA EJECUCIÓN", bg=COLORES["panel_suave"],
            fg=COLORES["texto_secundario"], font=("Segoe UI", 9, "bold"),
        ).pack(side="left")
        tk.Label(
            cabecera, text=estado, bg=COLORES["panel_suave"], fg=color,
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
            rejilla = tk.Frame(self.panel_resultado, bg=COLORES["panel_suave"])
            rejilla.pack(fill="x", padx=10, pady=(2, 8))
            for indice, (nombre, valor) in enumerate(disponibles):
                tarjeta = tk.Frame(
                    rejilla, bg=COLORES["panel"], highlightbackground=COLORES["borde"],
                    highlightthickness=1,
                )
                tarjeta.grid(row=indice // 3, column=indice % 3, sticky="nsew", padx=4, pady=4)
                tk.Label(
                    tarjeta, text=nombre, bg=COLORES["panel"], fg=COLORES["texto_secundario"],
                    font=("Segoe UI", 8),
                ).pack(anchor="w", padx=10, pady=(8, 2))
                tk.Label(
                    tarjeta, text=str(valor), bg=COLORES["panel"], fg=COLORES["texto"],
                    font=("Segoe UI", 11, "bold"),
                ).pack(anchor="w", padx=10, pady=(0, 8))
            for columna in range(3):
                rejilla.grid_columnconfigure(columna, weight=1)

        archivos = resultado.get("archivos_generados", [])
        if archivos:
            tk.Label(
                self.panel_resultado, text=f"Informe: {archivos[0]}",
                wraplength=760, justify="left", bg=COLORES["panel_suave"],
                fg=COLORES["primario"], font=("Segoe UI", 8),
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
        if self.en_ejecucion and self.preferencias.obtener("confirmar_cierre", True):
            if not messagebox.askyesno(
                "Cerrar",
                "Hay un proceso en ejecución. ¿Desea cerrar de todas formas?",
            ):
                return

        try:
            cambios = {}
            if self.preferencias.obtener("recordar_ventana", True):
                cambios["geometria"] = self.geometry()
                cambios["estado_ventana"] = self.state()
            if self.preferencias.obtener("recordar_sidebar", True):
                cambios["sidebar_colapsada"] = bool(self.sidebar.colapsada)
            if cambios:
                self.preferencias.actualizar(cambios)
        except Exception:
            pass

        self.destroy()
