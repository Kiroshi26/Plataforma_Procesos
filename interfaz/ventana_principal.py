import os
import subprocess
import sys
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any, Dict

import customtkinter as ctk

from interfaz.estilos import COLORES, FUENTE, aplicar_tema
from interfaz.paginas.configuracion import PaginaConfiguracion
from interfaz.paginas.dashboard import DashboardPage
from interfaz.paginas.monitoreo import PaginaMonitoreo
from interfaz.paginas.procesos import PaginaProcesos
from interfaz.vistas_procesos import (
    VistaComisiones,
    VistaCruceEfectivo,
    VistaInversiones,
    abrir_archivo_o_carpeta,
)
from interfaz.widgets.sidebar import Sidebar
from nucleo.ejecutor import ejecutar_proyecto
from nucleo.gestor_preferencias import GestorPreferencias
from nucleo.historial_ejecuciones import HistorialEjecuciones

MESES = [
    ("Enero", 1),
    ("Febrero", 2),
    ("Marzo", 3),
    ("Abril", 4),
    ("Mayo", 5),
    ("Junio", 6),
    ("Julio", 7),
    ("Agosto", 8),
    ("Septiembre", 9),
    ("Octubre", 10),
    ("Noviembre", 11),
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
        
        self.pagina_monitoreo_cache = None

        self.title("Bancolombia | Aplicativo de Procesos")
        geo = self.preferencias.obtener("geometria", "1280x800")
        if not self.preferencias.obtener("recordar_ventana", True):
            geo = "1280x800"

        if "+" in geo:
            geo = geo.split("+")[0]
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

        # Footer corporativo de seguridad
        pie = ctk.CTkFrame(self.panel_principal, fg_color="transparent")
        pie.pack(side="bottom", fill="x", padx=36, pady=(0, 16))

        ctk.CTkLabel(
            pie,
            text="💡  Mantén tus credenciales seguras y no compartas los resultados fuera de los canales autorizados.",
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 12),
        ).pack(side="left")

        ctk.CTkLabel(
            pie,
            text="Seguridad   |   Confidencialidad   |   Integridad",
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 11),
        ).pack(side="right")

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

    def _limpiar_panel(self):
        for elemento in self.contenedor_paginas.winfo_children():
            elemento.destroy()
        self.campos = {}

    def _mostrar_inicio(self):
        self._limpiar_panel()

        dashboard = DashboardPage(
        self.contenedor_paginas,
        self.registro,
        self._abrir_proyecto_desde_catalogo
    )

        dashboard.pack(fill="both", expand=True)

    def _mostrar_procesos(self):
        self._limpiar_panel()
        pagina = PaginaProcesos(self.contenedor_paginas, self.registro, self._abrir_proyecto_desde_catalogo)
        pagina.pack(fill="both", expand=True)

    def _mostrar_monitoreo(self):
        self._limpiar_panel()

        pagina = PaginaMonitoreo(
          self.contenedor_paginas,
          self.historial
    )

        pagina.pack(fill="both", expand=True)

    def _mostrar_configuracion(self):
        self._limpiar_panel()
        pagina = PaginaConfiguracion(
            self.contenedor_paginas,
            self.preferencias,
            self.configuracion.get("version", "0.5.0"),
            len(self.registro.listar()),
            on_guardar=self._aplicar_preferencias_en_ejecucion,
        )
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
        for widget in self.winfo_children():
            widget.destroy()

        self.configure(fg_color=COLORES["fondo"])
        self._construir_contenido()

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
        self._seleccionar_proyecto(identificador)


    def _construir_pie(self):
        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.pack(fill="x", padx=20, pady=(0, 12))
        self.estado_global = ctk.CTkLabel(pie, text="Listo", text_color=COLORES["texto_secundario"], font=(FUENTE, 12))
        self.estado_global.pack(side="left")
        ctk.CTkLabel(pie, text="No se publican resultados corporativos desde esta fase.", text_color=COLORES["texto_secundario"], font=(FUENTE, 12)).pack(side="right")

    def _limpiar_panel(self):
         for elemento in self.contenedor_paginas.winfo_children():
             elemento.destroy()
         self.campos = {}

    def _seleccionar_proyecto(self, identificador):
        if self.en_ejecucion:
            messagebox.showwarning("Proceso en ejecución", "Espere a que termine la ejecución actual.")
            return

        self.proyecto_actual = self.registro.obtener(identificador)
        self.ultimo_resultado = None
        self._limpiar_panel()

        self.scroll = ctk.CTkScrollableFrame(self.contenedor_paginas, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        # 1. Vista Especializada para Comisiones
        if identificador == "comisiones":
            vista = VistaComisiones(
                self.scroll,
                self.proyecto_actual,
                self._ejecutar_desde_vista,
                self._escribir_consola,
            )
            vista.pack(fill="both", expand=True)
            self._construir_consola_inferior(self.scroll)
            return

        # 2. Vista Especializada para Inversiones
        if identificador == "inversiones":
            vista = VistaInversiones(
                self.scroll,
                self.proyecto_actual,
                self._ejecutar_desde_vista,
                self._escribir_consola,
            )
            vista.pack(fill="both", expand=True)
            self._construir_consola_inferior(self.scroll)
            return

        # 3. Vista Especializada para Cruce de Efectivo
        if identificador == "cruce_efectivo":
            vista = VistaCruceEfectivo(
                self.scroll,
                self.proyecto_actual,
                self._ejecutar_desde_vista,
                self._escribir_consola,
            )
            vista.pack(fill="both", expand=True)
            self._construir_consola_inferior(self.scroll)
            return

        # 4. Fallback Dinámico Genérico para nuevos módulos
        self._construir_vista_generica(self.scroll)

    def _construir_consola_inferior(self, contenedor):
        if not self.preferencias.obtener("mostrar_consola", True):
            return

        frame_consola = ctk.CTkFrame(contenedor, fg_color="transparent")
        frame_consola.pack(fill="x", padx=28, pady=(16, 24))

        ctk.CTkLabel(
            frame_consola,
            text="Registro de eventos (Consola)",
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 12, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        self.consola = ctk.CTkTextbox(
            frame_consola,
            height=160,
            fg_color=COLORES["consola"],
            text_color=COLORES["consola_texto"],
            font=("Consolas", 11),
        )
        self.consola.pack(fill="x")
        self.consola.configure(state="disabled")

    def _ejecutar_desde_vista(self, parametros, callback_progreso, callback_finalizar):
        if self.en_ejecucion:
            messagebox.showwarning("Proceso en ejecución", "Espere a que termine la ejecución actual.")
            return

        self.en_ejecucion = True
        try:
            self.ejecucion_historial_actual = self.historial.iniciar(
                self.proyecto_actual.obtener_metadatos(), parametros
            )
        except Exception as error:
            self.ejecucion_historial_actual = None
            self._escribir_consola(f"[ADVERTENCIA] No fue posible iniciar el historial: {error}")

        def hilo_trabajo():
            def rep_evento(estado, mensaje, porcentaje):
                self.after(0, lambda: callback_progreso(estado, mensaje, porcentaje))
                self.after(0, lambda: self._aplicar_evento(estado, mensaje, porcentaje))

            try:
                resultado = ejecutar_proyecto(self.proyecto_actual, parametros, rep_evento)
            except Exception as error:
                resultado = {
                    "exitoso": False,
                    "estado": "ERROR",
                    "mensaje": str(error),
                    "errores": [str(error)],
                }

            self.after(0, lambda: self._finalizar_ejecucion_desde_vista(resultado, callback_finalizar))

        hilo = threading.Thread(target=hilo_trabajo, daemon=True)
        hilo.start()

    def _finalizar_ejecucion_desde_vista(self, resultado, callback_finalizar):
        self.ultimo_resultado = resultado
        self.en_ejecucion = False
        self._escribir_consola(f"Estado final: {resultado.get('estado')}")
        self._escribir_consola(resultado.get("mensaje", ""))
        for adv in resultado.get("advertencias", []):
            self._escribir_consola(f"[ADVERTENCIA] {adv}")
        for err in resultado.get("errores", []):
            self._escribir_consola(f"[ERROR] {err}")

        try:
            self.historial.finalizar(self.ejecucion_historial_actual, resultado)
        except Exception as error:
            self._escribir_consola(f"[ADVERTENCIA] No fue posible finalizar el historial: {error}")
        finally:
            self.ejecucion_historial_actual = None

        callback_finalizar(resultado)

        archivos = resultado.get("archivos_generados", [])
        if resultado.get("exitoso"):
            messagebox.showinfo("Ejecución Exitosa", resultado.get("mensaje", "Proceso finalizado."))
            if self.preferencias.obtener("abrir_resultado_automaticamente", False) and archivos:
                abrir_archivo_o_carpeta(archivos[0])
        else:
            messagebox.showwarning("Ejecución con Alertas", resultado.get("mensaje", "Proceso finalizado con observaciones."))

    def _aplicar_evento(self, estado, mensaje, porcentaje):
        self._escribir_consola(f"[{estado}] {mensaje}")
        try:
            if self.ejecucion_historial_actual:
                self.historial.agregar_evento(self.ejecucion_historial_actual, estado, mensaje, porcentaje)
        except Exception:
            pass

    def _escribir_consola(self, texto):
        if not hasattr(self, "consola") or not self.consola.winfo_exists():
            return
        self.consola.configure(state="normal")
        self.consola.insert("end", texto + "\n")
        self.consola.see("end")
        self.consola.configure(state="disabled")

    def _construir_vista_generica(self, contenedor):
        metadatos = self.proyecto_actual.obtener_metadatos()
        disponibilidad = self.proyecto_actual.validar_disponibilidad()

        cabecera = ctk.CTkFrame(contenedor, fg_color="transparent")
        cabecera.pack(fill="x", padx=30, pady=(26, 12))
        ctk.CTkLabel(cabecera, text=metadatos["nombre"], text_color=COLORES["texto"], font=(FUENTE, 30, "bold")).pack(anchor="w")
        ctk.CTkLabel(cabecera, text=metadatos["descripcion"], text_color=COLORES["texto_secundario"], font=(FUENTE, 14)).pack(anchor="w", pady=(4, 0))

        color_disp = COLORES["verde"] if disponibilidad["disponible"] else COLORES["rojo"]
        ctk.CTkLabel(cabecera, text=disponibilidad["mensaje"], text_color=color_disp, font=(FUENTE, 13, "bold")).pack(anchor="w", pady=(8, 0))

        formulario = ctk.CTkFrame(contenedor, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
        formulario.pack(fill="x", padx=30, pady=10)

        formulario.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(formulario, text="Configuración del proceso", text_color=COLORES["texto"], font=(FUENTE, 16, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(14, 1))
        ctk.CTkLabel(formulario, text="Define los parámetros necesarios antes de ejecutar.", text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).grid(row=1, column=0, columnspan=3, sticky="w", padx=16, pady=(0, 7))
        for fila, campo in enumerate(self.proyecto_actual.obtener_campos_configuracion(), start=2):
            self._crear_campo(formulario, fila, campo)

        acciones = ctk.CTkFrame(contenedor, fg_color="transparent")
        acciones.pack(fill="x", padx=30, pady=(12, 8))

        self.boton_ejecutar = ctk.CTkButton(
            acciones,
            text="Ejecutar módulo",
            command=self._ejecutar_generico,
            fg_color=COLORES["primario"],
            text_color=COLORES["texto_boton"],
            hover_color=COLORES["primario_hover"],
            font=(FUENTE, 13, "bold"),
        )
        self.boton_ejecutar.pack(side="left")

        self.progreso = ctk.CTkProgressBar(contenedor, mode="determinate", progress_color=COLORES["verde"])
        self.progreso.set(0)
        self.progreso.pack(fill="x", padx=30, pady=(20, 4))

        self.etiqueta_progreso = ctk.CTkLabel(contenedor, text="Esperando ejecución...", text_color=COLORES["texto_secundario"], font=(FUENTE, 12))
        self.etiqueta_progreso.pack(fill="x", padx=30)

        self._construir_consola_inferior(contenedor)

    def _crear_campo(self, padre, fila, campo):
        padre.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(padre, text=campo["etiqueta"], text_color=COLORES["texto"], font=(FUENTE, 13)).grid(row=fila, column=0, sticky="w", padx=(16, 16), pady=10)

        tipo = campo["tipo"]
        variable = ctk.StringVar()
        
                # ----------------------------------
        # NUEVO: LISTAS DESPLEGABLES
        # ----------------------------------

        if tipo == "opcion":
            opciones = campo.get("opciones", [])
            if opciones:
                variable.set(opciones[0])
            control = ctk.CTkOptionMenu(
                padre,
                variable=variable,
                values=opciones,
                fg_color=COLORES["panel"],
                text_color=COLORES["texto"],
                button_color=COLORES["primario"],
                button_hover_color=COLORES["primario_hover"],
            )
            control.grid(row=fila, column=1, sticky="ew", padx=(0, 16), pady=10)
            self.campos[campo["id"]] = {"variable": variable, "tipo": tipo}
            return

        if tipo == "password":
            control = ctk.CTkEntry(padre, textvariable=variable, show="*", fg_color=COLORES["panel"], text_color=COLORES["texto"])
            control.grid(row=fila, column=1, sticky="ew", padx=(0, 16), pady=10)
            self.campos[campo["id"]] = {"variable": variable, "tipo": tipo, "sensible": True}
            return

        if tipo == "archivo_excel":
            control = ctk.CTkEntry(padre, textvariable=variable, fg_color=COLORES["panel"], text_color=COLORES["texto"])
            control.grid(row=fila, column=1, sticky="ew", padx=(0, 8), pady=10)
            ctk.CTkButton(
                padre,
                text="Examinar...",
                command=lambda var=variable: self._seleccionar_archivo_excel(var),
                fg_color=COLORES["panel_suave"],
                text_color=COLORES["texto"],
                hover_color=COLORES["borde"],
                font=(FUENTE, 12),
            ).grid(row=fila, column=2, padx=(0, 16), pady=10)
            self.campos[campo["id"]] = {"variable": variable, "tipo": tipo}
            return

        if tipo == "carpeta":
            control = ctk.CTkEntry(padre, textvariable=variable, fg_color=COLORES["panel"], text_color=COLORES["texto"])
            control.grid(row=fila, column=1, sticky="ew", padx=(0, 8), pady=10)
            ctk.CTkButton(
                padre,
                text="Examinar...",
                command=lambda var=variable: self._seleccionar_carpeta(var),
                fg_color=COLORES["panel_suave"],
                text_color=COLORES["texto"],
                hover_color=COLORES["borde"],
                font=(FUENTE, 12),
            ).grid(row=fila, column=2, padx=(0, 16), pady=10)
            self.campos[campo["id"]] = {"variable": variable, "tipo": tipo}
            return

        if tipo == "booleano":
            variable.set("0")
            control = ctk.CTkCheckBox(padre, text="", variable=variable, onvalue="1", offvalue="0")
            control.grid(row=fila, column=1, sticky="w", padx=(0, 16), pady=10)
            self.campos[campo["id"]] = {"variable": variable, "tipo": tipo}
            return

        control = ctk.CTkEntry(padre, textvariable=variable, fg_color=COLORES["panel"], text_color=COLORES["texto"])
        control.grid(row=fila, column=1, sticky="ew", padx=(0, 16), pady=10)
        self.campos[campo["id"]] = {"variable": variable, "tipo": tipo}
        
    def _seleccionar_carpeta(self, variable):
        ruta = filedialog.askdirectory(title="Seleccione una carpeta local")
        if ruta:
            variable.set(ruta)

    def _seleccionar_archivo_excel(self, variable):
        ruta = filedialog.askopenfilename(
            title="Seleccione un archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xlsm *.xlsb *.xls"), ("Todos los archivos", "*.*")],
        )
        if ruta:
            variable.set(ruta)

    def _ejecutar_generico(self):
        parametros = {}
        for identificador, campo in self.campos.items():
            if campo["tipo"] == "booleano":
                parametros[identificador] = campo["variable"].get() == "1"
            else:
                parametros[identificador] = campo["variable"].get().strip()

        errores = self.proyecto_actual.validar_parametros(parametros)
        if errores:
            messagebox.showwarning("Validación", "\n".join(f"• {e}" for e in errores))
            return

        def progreso_cb(estado, mensaje, pct):
            self.progreso.set(pct / 100.0)
            self.etiqueta_progreso.configure(text=f"[{estado}] {mensaje}")

        def fin_cb(res):
            self.boton_ejecutar.configure(state="normal")
            self.progreso.set(1.0 if res.get("exitoso") else 0.0)
            self.etiqueta_progreso.configure(text=res.get("mensaje", "Finalizado."))

        self.boton_ejecutar.configure(state="disabled")
        self._ejecutar_desde_vista(parametros, progreso_cb, fin_cb)

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
            if cambios:
                self.preferencias.actualizar(cambios)
        except Exception:
            pass

        self.destroy()
