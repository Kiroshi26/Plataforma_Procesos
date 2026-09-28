import os
import subprocess
import sys
import threading
from datetime import date
import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
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

class VentanaPrincipal(ctk.CTk):
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

        self.title("Bancolombia | Aplicativo de Procesos")
        geo = self.preferencias.obtener("geometria", "1280x800")
        if not self.preferencias.obtener("recordar_ventana", True): geo = "1280x800"
        
        # Corrección por posible bug al leer geometría
        if "+" in geo: geo = geo.split("+")[0]
        self.geometry(geo)
        
        self.minsize(1024, 720)
        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self.configure(fg_color=COLORES["fondo"])

        self._construir_contenido()
        
        try:
            if self.preferencias.obtener("recordar_ventana", True) and self.preferencias.obtener("estado_ventana") == "zoomed":
                self.state("zoomed")
        except Exception:
            pass
            
        self.sidebar.seleccionar("inicio", notificar=False)
        self._mostrar_inicio()

    def _construir_contenido(self):
        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True)

        self.sidebar = Sidebar(cuerpo, on_navegar=self._navegar)
        self.sidebar.pack(side="left", fill="y")

        self.panel_principal = ctk.CTkFrame(cuerpo, fg_color=COLORES["fondo"], corner_radius=0)
        self.panel_principal.pack(side="left", fill="both", expand=True)

        self.contenedor_paginas = ctk.CTkFrame(self.panel_principal, fg_color="transparent")
        self.contenedor_paginas.pack(side="top", fill="both", expand=True)

        # Footer de seguridad
        pie = ctk.CTkFrame(self.panel_principal, fg_color="transparent")
        pie.pack(side="bottom", fill="x", padx=36, pady=(0, 20))
        
        ctk.CTkLabel(pie, text="💡  Recuerda mantener tus credenciales seguras y no compartir los resultados fuera de los canales autorizados.", text_color=COLORES["texto_secundario"], font=(FUENTE, 12)).pack(side="left")
        ctk.CTkLabel(pie, text="Seguridad   |   Confidencialidad   |   Integridad", text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(side="right")

    def _navegar(self, pagina):
        if self.en_ejecucion and pagina != self.pagina_actual:
            if not messagebox.askyesno("Proceso en ejecución", "Hay un proceso en ejecución. ¿Desea cambiar de vista sin detenerlo?"):
                self.sidebar.seleccionar(self.pagina_actual, notificar=False)
                return

        self.pagina_actual = pagina
        self.sidebar.seleccionar(pagina, notificar=False)

        if pagina == "inicio": self._mostrar_inicio()
        elif pagina == "procesos": self._mostrar_procesos()
        elif pagina == "monitoreo": self._mostrar_monitoreo()
        elif pagina == "configuracion": self._mostrar_configuracion()

    def _limpiar_panel(self):
        for elemento in self.contenedor_paginas.winfo_children():
            elemento.destroy()
        self.campos = {}

    def _mostrar_inicio(self):
        self._limpiar_panel()
        dashboard = DashboardPage(self.contenedor_paginas, self.registro, self._abrir_proyecto_desde_catalogo)
        dashboard.pack(fill="both", expand=True)

    def _mostrar_procesos(self):
        self._limpiar_panel()
        pagina = PaginaProcesos(self.contenedor_paginas, self.registro, self._abrir_proyecto_desde_catalogo)
        pagina.pack(fill="both", expand=True)

    def _mostrar_monitoreo(self):
<<<<<<< HEAD
<<<<<<< Updated upstream
=======
>>>>>>> 6453774 (UI: rediseño completo de la interfaz según mockup referencial)
        for widget in self.contenedor_paginas.winfo_children():
            widget.pack_forget()

        pagina = self.pagina_monitoreo_cache
        if pagina is None or not pagina.winfo_exists():
            pagina = PaginaMonitoreo(self.contenedor_paginas, self.historial)
            self.pagina_monitoreo_cache = pagina

=======
        self._limpiar_panel()
        pagina = PaginaMonitoreo(self.panel_principal, self.historial)
>>>>>>> Stashed changes
        pagina.pack(fill="both", expand=True)

    def _mostrar_configuracion(self):
        self._limpiar_panel()
        pagina = PaginaConfiguracion(self.contenedor_paginas, self.preferencias, self.configuracion.get("version", "0.4.0"), len(self.registro.listar()), on_guardar=self._aplicar_preferencias_en_ejecucion)
        pagina.pack(fill="both", expand=True)

    def _aplicar_preferencias_en_ejecucion(self, datos):
        if self.en_ejecucion:
            messagebox.showwarning("Configuración", "El tema no puede cambiar mientras hay un proceso en ejecución.")
            return

        tema_anterior = COLORES.copy()
        aplicar_tema(datos.get("tema", "claro"))
        if tema_anterior != COLORES:
            self._reconstruir_interfaz("configuracion")

    def _reconstruir_interfaz(self, pagina_destino="inicio"):
        for widget in self.winfo_children(): widget.destroy()
        
        self.configure(fg_color=COLORES["fondo"])
        self._construir_contenido()

        self.pagina_actual = pagina_destino
        self.sidebar.seleccionar(pagina_destino, notificar=False)
        if pagina_destino == "configuracion": self._mostrar_configuracion()
        elif pagina_destino == "monitoreo": self._mostrar_monitoreo()
        elif pagina_destino == "procesos": self._mostrar_procesos()
        else: self._mostrar_inicio()

    def _abrir_proyecto_desde_catalogo(self, identificador):
        self.pagina_actual = "procesos"
        self.sidebar.seleccionar("procesos", notificar=False)
        self._seleccionar_proyecto(identificador)

<<<<<<< HEAD
<<<<<<< Updated upstream
=======
    def _construir_pie(self):
        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.pack(fill="x", padx=20, pady=(0, 12))
        self.estado_global = ctk.CTkLabel(pie, text="Listo", text_color=COLORES["texto_secundario"], font=(FUENTE, 12))
        self.estado_global.pack(side="left")
        ctk.CTkLabel(pie, text="No se publican resultados corporativos desde esta fase.", text_color=COLORES["texto_secundario"], font=(FUENTE, 12)).pack(side="right")

    def _limpiar_panel(self):
        for elemento in self.panel_principal.winfo_children():
            elemento.destroy()
        self.campos = {}

    def _mostrar_inicio(self):
        self._limpiar_panel()
        dashboard = DashboardPage(self.panel_principal, self.registro, self._abrir_proyecto_desde_catalogo)
        dashboard.pack(fill="both", expand=True)

>>>>>>> Stashed changes
=======
>>>>>>> 6453774 (UI: rediseño completo de la interfaz según mockup referencial)
    def _seleccionar_proyecto(self, identificador):
        if self.en_ejecucion:
            messagebox.showwarning("Proceso en ejecución", "Espere a que termine la ejecución actual.")
            return

        self.proyecto_actual = self.registro.obtener(identificador)
        self.ultimo_resultado = None
        metadatos = self.proyecto_actual.obtener_metadatos()
        disponibilidad = self.proyecto_actual.validar_disponibilidad()
        self._limpiar_panel()

        self.scroll = ctk.CTkScrollableFrame(self.contenedor_paginas, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        cabecera = ctk.CTkFrame(self.scroll, fg_color="transparent")
        cabecera.pack(fill="x", padx=30, pady=(26, 12))
        ctk.CTkLabel(cabecera, text=metadatos["nombre"], text_color=COLORES["texto"], font=(FUENTE, 30, "bold")).pack(anchor="w")
        ctk.CTkLabel(cabecera, text=metadatos["descripcion"], text_color=COLORES["texto_secundario"], font=(FUENTE, 14)).pack(anchor="w", pady=(4, 0))

        color_disp = COLORES["verde"] if disponibilidad["disponible"] else COLORES["rojo"]
        ctk.CTkLabel(cabecera, text=disponibilidad["mensaje"], text_color=color_disp, font=(FUENTE, 13, "bold")).pack(anchor="w", pady=(8, 0))

<<<<<<< HEAD
<<<<<<< Updated upstream
        formulario = ctk.CTkFrame(self.scroll, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
=======
        formulario = ctk.CTkFrame(self.scroll, fg_color=COLORES["panel"], corner_radius=14, border_width=1, border_color=COLORES["borde"])
>>>>>>> Stashed changes
=======
        formulario = ctk.CTkFrame(self.scroll, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
>>>>>>> 6453774 (UI: rediseño completo de la interfaz según mockup referencial)
        formulario.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(formulario, text="Configuración del proceso", text_color=COLORES["texto"], font=(FUENTE, 16, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(14, 1))
        ctk.CTkLabel(formulario, text="Define los parámetros necesarios antes de ejecutar.", text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).grid(row=1, column=0, columnspan=3, sticky="w", padx=16, pady=(0, 7))
        for fila, campo in enumerate(self.proyecto_actual.obtener_campos_configuracion(), start=2):
            self._crear_campo(formulario, fila, campo)

        acciones = ctk.CTkFrame(self.scroll, fg_color="transparent")
        acciones.pack(fill="x", padx=30, pady=(12, 8))
        
        ctk.CTkButton(acciones, text="Validar parámetros", command=self._validar, fg_color=COLORES["panel_suave"], text_color=COLORES["texto"], hover_color=COLORES["borde"], font=(FUENTE, 13)).pack(side="left")
<<<<<<< Updated upstream
        self.boton_ejecutar = ctk.CTkButton(acciones, text="Ejecutar módulo", command=self._ejecutar, fg_color=COLORES["primario"], text_color=COLORES["texto_boton"], hover_color=COLORES["primario_hover"], font=(FUENTE, 13, "bold"))
=======
        self.boton_ejecutar = ctk.CTkButton(acciones, text="Ejecutar proceso  →", command=self._ejecutar, fg_color=COLORES["primario"], text_color="#111111", hover_color=COLORES["primario_hover"], font=(FUENTE, 13, "bold"))
>>>>>>> Stashed changes
        self.boton_ejecutar.pack(side="left", padx=8)
        ctk.CTkButton(acciones, text="Abrir carpeta local", command=self._abrir_carpeta, fg_color=COLORES["panel_suave"], text_color=COLORES["texto"], hover_color=COLORES["borde"], font=(FUENTE, 13)).pack(side="left")
        
        self.boton_abrir_archivo = ctk.CTkButton(acciones, text="Abrir informe", command=self._abrir_ultimo_archivo, state="disabled", fg_color=COLORES["panel_suave"], text_color=COLORES["texto"], font=(FUENTE, 13))
        self.boton_abrir_archivo.pack(side="left", padx=8)

        self.progreso = ctk.CTkProgressBar(self.scroll, mode="determinate", progress_color=COLORES["verde"])
        self.progreso.set(0)
        self.progreso.pack(fill="x", padx=30, pady=(20, 4))

        self.etiqueta_progreso = ctk.CTkLabel(self.scroll, text="Esperando validación...", text_color=COLORES["texto_secundario"], font=(FUENTE, 12))
        self.etiqueta_progreso.pack(fill="x", padx=30)

        self.consola = ctk.CTkTextbox(self.scroll, height=180, corner_radius=12, fg_color=COLORES["consola"], text_color=COLORES["consola_texto"], font=("Consolas", 12))
        if self.preferencias.obtener("mostrar_consola", True):
            self.consola.pack(fill="x", padx=30, pady=(12, 8))
            self.consola.configure(state="disabled")

<<<<<<< HEAD
<<<<<<< Updated upstream
        self.panel_resultado = ctk.CTkFrame(self.scroll, fg_color=COLORES["panel_suave"], border_width=1, border_color=COLORES["borde"], corner_radius=12)
=======
        self.panel_resultado = ctk.CTkFrame(self.scroll, fg_color=COLORES["panel_suave"], corner_radius=14, border_width=1, border_color=COLORES["borde"])
>>>>>>> Stashed changes
=======
        self.panel_resultado = ctk.CTkFrame(self.scroll, fg_color=COLORES["panel_suave"], border_width=1, border_color=COLORES["borde"], corner_radius=12)
>>>>>>> 6453774 (UI: rediseño completo de la interfaz según mockup referencial)
        self.panel_resultado.pack(fill="x", padx=30, pady=(10, 24))
        ctk.CTkLabel(self.panel_resultado, text="El resumen de la última ejecución aparecerá aquí.", text_color=COLORES["texto_secundario"], font=(FUENTE, 12)).pack(anchor="w", padx=14, pady=12)
        
        self._escribir_consola("Módulo cargado. No se ha ejecutado ningún motor.")

    def _crear_campo(self, padre, fila, campo):
        padre.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(padre, text=campo["etiqueta"], text_color=COLORES["texto"], font=(FUENTE, 13)).grid(row=fila, column=0, sticky="w", padx=(16, 16), pady=10)

        tipo = campo["tipo"]
        variable = ctk.StringVar()

        if campo["id"] == "anio": variable.set(str(date.today().year))
        elif campo["id"] == "mes": variable.set("7")
        elif campo["id"] == "periodo": variable.set("")
        if campo["id"] == "periodo" and self.proyecto_actual.obtener_metadatos().get("id") == "inversiones":
            hoy = date.today(); mes_ref = hoy.month - 1; anio_ref = hoy.year
            if mes_ref == 0: mes_ref = 12; anio_ref -= 1
            anios = [str(x) for x in range(hoy.year - 3, hoy.year + 3)]
            variable_anio = ctk.StringVar(value=str(anio_ref))
            variable_mes = ctk.StringVar(value=next(n for n, m in MESES if m == mes_ref))
            box = ctk.CTkFrame(padre, fg_color="transparent"); box.grid(row=fila, column=1, sticky="ew", padx=(0,16), pady=10); box.grid_columnconfigure((0,1), weight=1)
            ctk.CTkOptionMenu(box, variable=variable_anio, values=anios, fg_color=COLORES["panel"], text_color=COLORES["texto"], button_color=COLORES["primario"], button_hover_color=COLORES["primario_hover"]).grid(row=0,column=0,sticky="ew",padx=(0,6))
            ctk.CTkOptionMenu(box, variable=variable_mes, values=[n for n,_ in MESES], fg_color=COLORES["panel"], text_color=COLORES["texto"], button_color=COLORES["primario"], button_hover_color=COLORES["primario_hover"]).grid(row=0,column=1,sticky="ew",padx=(6,0))
            self.campos[campo["id"]] = {"variable":variable,"anio_visual":variable_anio,"mes_visual":variable_mes,"tipo":"periodo_inversiones"}
            return
        if tipo == "mes":
            variable_visual = ctk.StringVar(value="Julio")
            control = ctk.CTkOptionMenu(padre, variable=variable_visual, values=[nombre for nombre, _ in MESES], fg_color=COLORES["panel"], text_color=COLORES["texto"], button_color=COLORES["primario"], button_hover_color=COLORES["primario_hover"])
            control.grid(row=fila, column=1, sticky="ew", padx=(0, 16), pady=10)
            self.campos[campo["id"]] = {"variable": variable, "visual": variable_visual, "tipo": tipo}
            return

        if tipo == "password":
            control = ctk.CTkEntry(padre, textvariable=variable, show="*", fg_color=COLORES["panel"], text_color=COLORES["texto"])
            control.grid(row=fila, column=1, sticky="ew", padx=(0, 16), pady=10)
            self.campos[campo["id"]] = {"variable": variable, "tipo": tipo, "sensible": True}
            return

        if tipo == "archivo_excel":
            control = ctk.CTkEntry(padre, textvariable=variable, fg_color=COLORES["panel"], text_color=COLORES["texto"])
            control.grid(row=fila, column=1, sticky="ew", padx=(0, 8), pady=10)
            ctk.CTkButton(padre, text="Seleccionar archivo", command=lambda var=variable: self._seleccionar_archivo_excel(var), fg_color=COLORES["panel_suave"], text_color=COLORES["texto"], hover_color=COLORES["borde"], font=(FUENTE, 12)).grid(row=fila, column=2, padx=(0, 16), pady=10)
            self.campos[campo["id"]] = {"variable": variable, "tipo": tipo}
            return

        if tipo == "booleano":
            variable.set("0")
            state = "disabled" if campo.get("bloqueado") else "normal"
            control = ctk.CTkCheckBox(padre, text="", variable=variable, onvalue="1", offvalue="0", state=state)
            control.grid(row=fila, column=1, sticky="w", padx=(0, 16), pady=10)
        else:
            control = ctk.CTkEntry(padre, textvariable=variable, fg_color=COLORES["panel"], text_color=COLORES["texto"])
            control.grid(row=fila, column=1, sticky="ew", padx=(0, 8 if tipo == "carpeta" else 16), pady=10)

        if tipo == "carpeta":
            ctk.CTkButton(padre, text="Seleccionar", command=lambda var=variable: self._seleccionar_carpeta(var), fg_color=COLORES["panel_suave"], text_color=COLORES["texto"], hover_color=COLORES["borde"], font=(FUENTE, 12)).grid(row=fila, column=2, padx=(0, 16), pady=10)

        self.campos[campo["id"]] = {"variable": variable, "tipo": tipo}

    def _seleccionar_carpeta(self, variable):
        ruta = filedialog.askdirectory(title="Seleccione una carpeta local")
        if ruta: variable.set(ruta)

    def _seleccionar_archivo_excel(self, variable):
        ruta = filedialog.askopenfilename(title="Seleccione el archivo de cierre mensual", filetypes=[("Archivos Excel", "*.xlsx *.xlsm *.xlsb"), ("Todos los archivos", "*.*")])
        if ruta: variable.set(ruta)

    def _recoger_parametros(self):
        parametros = {}
        for identificador, campo in self.campos.items():
            if campo["tipo"] == "mes":
                nombre = campo["visual"].get()
                parametros[identificador] = dict(MESES)[nombre]
            elif campo["tipo"] == "periodo_inversiones":
                anio = campo["anio_visual"].get(); mes = dict(MESES)[campo["mes_visual"].get()]
                parametros[identificador] = f"{anio}-{mes:02d}"
            elif campo["tipo"] == "booleano":
                parametros[identificador] = campo["variable"].get() == "1"
            else:
                parametros[identificador] = campo["variable"].get().strip()
        return parametros

    def _validar(self):
        if self.proyecto_actual is None: return False
        errores = self.proyecto_actual.validar_parametros(self._recoger_parametros())
        if errores:
            self._escribir_consola("VALIDACIÓN CON ERRORES:")
            for error in errores: self._escribir_consola(f"  - {error}")
            messagebox.showwarning("Validación", "Revise los parámetros indicados en el registro.")
            return False
        self._escribir_consola("Parámetros válidos para la fase actual.")
        self.etiqueta_progreso.configure(text="Parámetros válidos.")
        return True

    def _ejecutar(self):
        if self.en_ejecucion or not self._validar(): return
        self.en_ejecucion = True
        self.boton_ejecutar.configure(state="disabled")
        self.progreso.set(0)
        parametros = self._recoger_parametros()
        try:
            self.ejecucion_historial_actual = self.historial.iniciar(self.proyecto_actual.obtener_metadatos(), parametros)
        except Exception as error:
            self.ejecucion_historial_actual = None
            self._escribir_consola(f"[ADVERTENCIA] No fue posible iniciar el historial: {error}")
        hilo = threading.Thread(target=self._ejecucion_en_segundo_plano, args=(parametros,), daemon=True)
        hilo.start()

    def _ejecucion_en_segundo_plano(self, parametros):
        try:
            resultado = ejecutar_proyecto(self.proyecto_actual, parametros, self._reportar_evento_desde_hilo)
            self.after(0, lambda: self._finalizar_ejecucion(resultado))
        except Exception as error:
            resultado = {"exitoso": False, "estado": "ERROR", "mensaje": str(error), "errores": [str(error)]}
            self.after(0, lambda: self._finalizar_ejecucion(resultado))

    def _reportar_evento_desde_hilo(self, estado, mensaje, porcentaje):
        self.after(0, lambda: self._aplicar_evento(estado, mensaje, porcentaje))

    def _aplicar_evento(self, estado, mensaje, porcentaje):
        self.progreso.set(porcentaje / 100.0)
        self.etiqueta_progreso.configure(text=f"{estado}: {mensaje}")
        self._escribir_consola(f"[{estado}] {mensaje}")
        try:
            self.historial.agregar_evento(self.ejecucion_historial_actual, estado, mensaje, porcentaje)
        except Exception: pass

    def _finalizar_ejecucion(self, resultado):
        self.ultimo_resultado = resultado
        self.en_ejecucion = False
        self.boton_ejecutar.configure(state="normal")
        self._escribir_consola(f"Estado final: {resultado.get('estado')}")
        self._escribir_consola(resultado.get("mensaje", ""))
        for advertencia in resultado.get("advertencias", []): self._escribir_consola(f"[ADVERTENCIA] {advertencia}")
        for error in resultado.get("errores", []): self._escribir_consola(f"[ERROR] {error}")
        
        self.etiqueta_progreso.configure(text=resultado.get("mensaje", "Proceso finalizado."))
        try:
            self.historial.finalizar(self.ejecucion_historial_actual, resultado)
        except Exception as error:
            self._escribir_consola(f"[ADVERTENCIA] No fue posible finalizar el historial: {error}")
        finally:
            self.ejecucion_historial_actual = None
            
        self._mostrar_resumen_resultado(resultado)
        archivos = resultado.get("archivos_generados", [])
        if archivos and hasattr(self, "boton_abrir_archivo"):
            self.boton_abrir_archivo.configure(state="normal")
            
        if resultado.get("exitoso"):
            self.progreso.set(1.0)
            messagebox.showinfo("Ejecución", resultado.get("mensaje", "Proceso finalizado."))
            if self.preferencias.obtener("abrir_resultado_automaticamente", False) and archivos:
                self._abrir_ultimo_archivo()
        else:
            messagebox.showwarning("Ejecución", resultado.get("mensaje", "Proceso no ejecutado."))

    def _escribir_consola(self, texto):
        if not hasattr(self, "consola"): return
        self.consola.configure(state="normal")
        self.consola.insert("end", texto + "\n")
        self.consola.see("end")
        self.consola.configure(state="disabled")

    def _abrir_carpeta(self):
        campo = self.campos.get("carpeta_salida")
        if not campo: return
        ruta = campo["variable"].get().strip()
        if not ruta:
            messagebox.showwarning("Carpeta", "Seleccione primero una carpeta local.")
            return
        carpeta = Path(ruta)
        if not carpeta.exists(): carpeta.mkdir(parents=True, exist_ok=True)
        try:
            if os.name == "nt": os.startfile(str(carpeta))
            elif sys.platform == "darwin": subprocess.Popen(["open", str(carpeta)])
            else: subprocess.Popen(["xdg-open", str(carpeta)])
        except Exception as error:
            messagebox.showerror("Carpeta", str(error))

    def _mostrar_resumen_resultado(self, resultado):
        if not hasattr(self, "panel_resultado"): return
        for elemento in self.panel_resultado.winfo_children(): elemento.destroy()

        estado = str(resultado.get("estado", "SIN ESTADO"))
        color = COLORES["verde"] if resultado.get("exitoso") else COLORES["amarillo"]
        if estado == "ERROR": color = COLORES["rojo"]

        cabecera = ctk.CTkFrame(self.panel_resultado, fg_color="transparent")
        cabecera.pack(fill="x", padx=14, pady=(12, 6))
        ctk.CTkLabel(cabecera, text="RESUMEN DE LA EJECUCIÓN", text_color=COLORES["texto_secundario"], font=(FUENTE, 12, "bold")).pack(side="left")
        ctk.CTkLabel(cabecera, text=estado, text_color=color, font=(FUENTE, 12, "bold")).pack(side="right")

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
            rejilla = ctk.CTkFrame(self.panel_resultado, fg_color="transparent")
            rejilla.pack(fill="x", padx=10, pady=(2, 8))
            for columna in range(3): rejilla.grid_columnconfigure(columna, weight=1)
            
            for indice, (nombre, valor) in enumerate(disponibles):
                tarjeta = ctk.CTkFrame(rejilla, fg_color=COLORES["panel"], border_width=1, border_color=COLORES["borde"], corner_radius=8)
                tarjeta.grid(row=indice // 3, column=indice % 3, sticky="nsew", padx=4, pady=4)
                ctk.CTkLabel(tarjeta, text=nombre, text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(anchor="w", padx=10, pady=(8, 2))
                ctk.CTkLabel(tarjeta, text=str(valor), text_color=COLORES["texto"], font=(FUENTE, 14, "bold")).pack(anchor="w", padx=10, pady=(0, 8))

        archivos = resultado.get("archivos_generados", [])
        if archivos:
            ctk.CTkLabel(self.panel_resultado, text=f"Informe: {archivos[0]}", wraplength=760, justify="left", text_color=COLORES["texto"], font=(FUENTE, 11)).pack(anchor="w", padx=14, pady=(0, 12))

    def _abrir_ultimo_archivo(self):
        if not self.ultimo_resultado: return
        archivos = self.ultimo_resultado.get("archivos_generados", [])
        if not archivos:
            messagebox.showwarning("Informe", "No hay un informe disponible.")
            return
        ruta = Path(archivos[0])
        if not ruta.exists():
            messagebox.showerror("Informe", f"No existe el archivo: {ruta}")
            return
        try:
            if os.name == "nt": os.startfile(str(ruta))
            elif sys.platform == "darwin": subprocess.Popen(["open", str(ruta)])
            else: subprocess.Popen(["xdg-open", str(ruta)])
        except Exception as error:
            messagebox.showerror("Informe", str(error))

    def _cerrar(self):
        if self.en_ejecucion and self.preferencias.obtener("confirmar_cierre", True):
            if not messagebox.askyesno("Cerrar", "Hay un proceso en ejecución. ¿Desea cerrar de todas formas?"):
                return

        try:
            cambios = {}
            if self.preferencias.obtener("recordar_ventana", True):
                cambios["geometria"] = self.geometry()
                cambios["estado_ventana"] = self.state()
            if self.preferencias.obtener("recordar_sidebar", True):
                cambios["sidebar_colapsada"] = bool(self.sidebar.colapsada)
            if cambios: self.preferencias.actualizar(cambios)
        except Exception: pass

        self.destroy()
