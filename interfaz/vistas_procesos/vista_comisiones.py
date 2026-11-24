# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
import threading

import customtkinter as ctk
from interfaz.estilos import COLORES, FUENTE
from interfaz.vistas_procesos.vista_base import (
    BadgePill,
    TarjetaSeccion,
    abrir_archivo_o_carpeta,
)

MESES_NOMBRES = [
    ("Enero", 1), ("Febrero", 2), ("Marzo", 3), ("Abril", 4),
    ("Mayo", 5), ("Junio", 6), ("Julio", 7), ("Agosto", 8),
    ("Septiembre", 9), ("Octubre", 10), ("Noviembre", 11), ("Diciembre", 12),
]


class VistaComisiones(ctk.CTkFrame):
    """Vista moderna especializada para el proceso de Comisiones 250115."""

    def __init__(self, parent, modulo, on_ejecutar, on_consola):
        super().__init__(parent, fg_color="transparent")
        self.modulo = modulo
        self.on_ejecutar = on_ejecutar
        self.on_consola = on_consola

        self.var_anio = ctk.StringVar(value=str(datetime.now().year))
        self.var_mes_nombre = ctk.StringVar(value="Julio")
        self.var_archivo_cierre = ctk.StringVar()
        self.var_carpeta_salida = ctk.StringVar(value=r"C:\Proyectos\Proyecto_Comisiones\salida")

        self.resultado_actual = None
        self._construir_ui()

    def _construir_ui(self):
        # Cabecera moderna
        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.pack(fill="x", padx=28, pady=(24, 12))

        fila_top = ctk.CTkFrame(cabecera, fg_color="transparent")
        fila_top.pack(fill="x")

        icono = ctk.CTkLabel(
            fila_top,
            text="🪙",
            width=54,
            height=54,
            corner_radius=12,
            fg_color=COLORES["fondo_modulo"],
            font=(FUENTE, 26),
        )
        icono.pack(side="left", padx=(0, 16))

        titulos = ctk.CTkFrame(fila_top, fg_color="transparent")
        titulos.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            titulos,
            text="Comisiones 250115",
            text_color=COLORES["texto"],
            font=(FUENTE, 24, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            titulos,
            text="Conciliación operativa mensual, liquidación de facturas y generación del informe informativo.",
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 13),
        ).pack(anchor="w", pady=(2, 0))

        BadgePill(fila_top, "MOTOR ACTIVO", "verde").pack(side="right", padx=6)

        # 1. Período
        card_periodo = TarjetaSeccion(self, "1. Período a Conciliar", "Selecciona el año y mes correspondiente al cierre.")
        fila_p = ctk.CTkFrame(card_periodo.cuerpo, fg_color="transparent")
        fila_p.pack(fill="x", pady=4)

        ctk.CTkLabel(fila_p, text="Año:", text_color=COLORES["texto"], font=(FUENTE, 13, "bold")).pack(side="left", padx=(0, 8))
        self.entry_anio = ctk.CTkEntry(fila_p, textvariable=self.var_anio, width=90, fg_color=COLORES["panel_suave"], text_color=COLORES["texto"])
        self.entry_anio.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(fila_p, text="Mes:", text_color=COLORES["texto"], font=(FUENTE, 13, "bold")).pack(side="left", padx=(0, 8))
        self.menu_mes = ctk.CTkOptionMenu(
            fila_p,
            variable=self.var_mes_nombre,
            values=[n for n, _ in MESES_NOMBRES],
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
            button_color=COLORES["primario"],
            button_hover_color=COLORES["primario_hover"],
            dropdown_text_color=COLORES["texto"],
            width=140,
        )
        self.menu_mes.pack(side="left", padx=(0, 20))

        # Botones rápidos
        ctk.CTkButton(
            fila_p,
            text="◀ Mes Anterior",
            command=self._establecer_mes_anterior,
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
            hover_color=COLORES["borde"],
            font=(FUENTE, 12),
            height=30,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            fila_p,
            text="Mes Actual",
            command=self._establecer_mes_actual,
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
            hover_color=COLORES["borde"],
            font=(FUENTE, 12),
            height=30,
        ).pack(side="left", padx=4)

        # 2. Archivo de Cierre Mensual
        card_archivo = TarjetaSeccion(self, "2. Archivo de Cierre Mensual", "Insumo operativo corporativo (.xlsx, .xlsm, .xlsb) con los movimientos del mes.")
        fila_a = ctk.CTkFrame(card_archivo.cuerpo, fg_color="transparent")
        fila_a.pack(fill="x", pady=4)

        self.entry_archivo = ctk.CTkEntry(
            fila_a,
            textvariable=self.var_archivo_cierre,
            placeholder_text="Seleccione el archivo de cierre mensual...",
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
        )
        self.entry_archivo.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            fila_a,
            text="Examinar...",
            command=self._seleccionar_archivo_cierre,
            fg_color=COLORES["primario"],
            text_color=COLORES["texto_boton"],
            hover_color=COLORES["primario_hover"],
            font=(FUENTE, 12, "bold"),
            width=110,
        ).pack(side="left")

        # Contenedor de pre-validación de hojas
        self.frame_hojas = ctk.CTkFrame(card_archivo.cuerpo, fg_color="transparent")
        self.frame_hojas.pack(fill="x", pady=(8, 0))
        self.lbl_validacion_archivo = ctk.CTkLabel(
            self.frame_hojas,
            text="Seleccione un archivo para verificar las hojas requeridas en vivo.",
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 11),
        )
        self.lbl_validacion_archivo.pack(anchor="w")

        # 3. Carpeta de Salida
        card_salida = TarjetaSeccion(self, "3. Carpeta Local de Salida", "Directorio donde se creará el informe Excel consolidado.")
        fila_s = ctk.CTkFrame(card_salida.cuerpo, fg_color="transparent")
        fila_s.pack(fill="x", pady=4)

        self.entry_salida = ctk.CTkEntry(
            fila_s,
            textvariable=self.var_carpeta_salida,
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
        )
        self.entry_salida.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            fila_s,
            text="Cambiar...",
            command=self._seleccionar_carpeta_salida,
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
            hover_color=COLORES["borde"],
            font=(FUENTE, 12),
            width=90,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            fila_s,
            text="Abrir Carpeta",
            command=lambda: abrir_archivo_o_carpeta(self.var_carpeta_salida.get()),
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
            hover_color=COLORES["borde"],
            font=(FUENTE, 12),
            width=100,
        ).pack(side="left")

        # 4. Panel de Acciones y Stepper
        self.card_accion = TarjetaSeccion(self, "4. Ejecución del Proceso", "Lanza el proceso completo en segundo plano sin congelar la interfaz.")

        fila_btn = ctk.CTkFrame(self.card_accion.cuerpo, fg_color="transparent")
        fila_btn.pack(fill="x", pady=4)

        self.btn_ejecutar = ctk.CTkButton(
            fila_btn,
            text="▶  Ejecutar Comisiones 250115",
            command=self._iniciar_ejecucion,
            fg_color=COLORES["primario"],
            text_color=COLORES["texto_boton"],
            hover_color=COLORES["primario_hover"],
            font=(FUENTE, 14, "bold"),
            height=40,
        )
        self.btn_ejecutar.pack(side="left", padx=(0, 12))

        self.btn_abrir_resultado = ctk.CTkButton(
            fila_btn,
            text="📊  Abrir Informe Generado",
            command=self._abrir_informe,
            state="disabled",
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
            hover_color=COLORES["borde"],
            font=(FUENTE, 13, "bold"),
            height=40,
        )
        self.btn_abrir_resultado.pack(side="left")

        # Barra de progreso
        self.progreso = ctk.CTkProgressBar(
            self.card_accion.cuerpo,
            mode="determinate",
            progress_color=COLORES["verde"],
            height=10,
        )
        self.progreso.set(0)
        self.progreso.pack(fill="x", pady=(14, 6))

        self.lbl_estado = ctk.CTkLabel(
            self.card_accion.cuerpo,
            text="Listo para iniciar.",
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 12),
        )
        self.lbl_estado.pack(anchor="w")

        # 5. Panel de Resumen de Resultados
        self.card_resultados = TarjetaSeccion(self, "5. Resumen de Ejecución", "Indicadores del informe procesado.")
        self.card_resultados.pack_forget()

    def _establecer_mes_anterior(self):
        ahora = datetime.now()
        mes = ahora.month - 1
        anio = ahora.year
        if mes == 0:
            mes = 12
            anio -= 1
        self.var_anio.set(str(anio))
        dict_meses = dict(MESES_NOMBRES)
        nombre = [k for k, v in dict_meses.items() if v == mes][0]
        self.var_mes_nombre.set(nombre)

    def _establecer_mes_actual(self):
        ahora = datetime.now()
        self.var_anio.set(str(ahora.year))
        dict_meses = dict(MESES_NOMBRES)
        nombre = [k for k, v in dict_meses.items() if v == ahora.month][0]
        self.var_mes_nombre.set(nombre)

    def _seleccionar_archivo_cierre(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de cierre mensual",
            filetypes=[("Archivos Excel", "*.xlsx *.xlsm *.xlsb"), ("Todos los archivos", "*.*")],
        )
        if ruta:
            self.var_archivo_cierre.set(ruta)
            self._inspeccionar_hojas(Path(ruta))

    def _inspeccionar_hojas(self, ruta: Path):
        for w in self.frame_hojas.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self.frame_hojas,
            text=f"Archivo: {ruta.name}  ({ruta.stat().st_size / (1024*1024):.1f} MB)",
            text_color=COLORES["texto"],
            font=(FUENTE, 11, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        hojas_requeridas = [
            "FACTURAS PENDIENTES", "PAGOS REALIZADOS", "FACTURAS REALIZADAS",
            "NOTAS REALIZADAS", "CAUSACIONES REALIZADAS"
        ]

        fila_pills = ctk.CTkFrame(self.frame_hojas, fg_color="transparent")
        fila_pills.pack(fill="x")

        def tarea_verificar():
            try:
                import openpyxl
                wb = openpyxl.load_workbook(ruta, read_only=True)
                hojas_encontradas = [h.upper() for h in wb.sheetnames]
                wb.close()
                self.after(0, lambda: self._mostrar_pills_hojas(fila_pills, hojas_requeridas, hojas_encontradas))
            except Exception as e:
                self.after(0, lambda: ctk.CTkLabel(fila_pills, text=f"No se pudieron leer las hojas: {e}", text_color=COLORES["rojo"], font=(FUENTE, 11)).pack(anchor="w"))

        threading.Thread(target=tarea_verificar, daemon=True).start()

    def _mostrar_pills_hojas(self, parent, requeridas, encontradas):
        for req in requeridas:
            presente = any(req in h for h in encontradas)
            BadgePill(
                parent,
                f"✓ {req}" if presente else f"✗ {req}",
                "verde" if presente else "amarillo",
            ).pack(side="left", padx=3, pady=2)

    def _seleccionar_carpeta_salida(self):
        ruta = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if ruta:
            self.var_carpeta_salida.set(ruta)

    def recoger_parametros(self):
        dict_meses = dict(MESES_NOMBRES)
        return {
            "anio": int(self.var_anio.get().strip()),
            "mes": dict_meses[self.var_mes_nombre.get()],
            "archivo_cierre": self.var_archivo_cierre.get().strip(),
            "carpeta_salida": self.var_carpeta_salida.get().strip(),
        }

    def _iniciar_ejecucion(self):
        parametros = self.recoger_parametros()
        errores = self.modulo.validar_parametros(parametros)
        if errores:
            messagebox.showwarning("Parámetros requeridos", "\n".join(f"• {e}" for e in errores))
            return

        self.btn_ejecutar.configure(state="disabled")
        self.btn_abrir_resultado.configure(state="disabled")
        self.progreso.set(0)
        self.lbl_estado.configure(text="Iniciando ejecución...")
        self.on_ejecutar(parametros, self._actualizar_progreso, self._finalizar)

    def _actualizar_progreso(self, estado, mensaje, porcentaje):
        self.progreso.set(porcentaje / 100.0)
        self.lbl_estado.configure(text=f"[{estado}] {mensaje}")

    def _finalizar(self, resultado):
        self.resultado_actual = resultado
        self.btn_ejecutar.configure(state="normal")

        archivos = resultado.get("archivos_generados", [])
        if archivos:
            self.btn_abrir_resultado.configure(state="normal")
            self.progreso.set(1.0)
            self.lbl_estado.configure(text="¡Informe final generado exitosamente!")
            self._mostrar_kpis_resultado(resultado)
        else:
            self.lbl_estado.configure(text=resultado.get("mensaje", "Proceso finalizado."))

    def _mostrar_kpis_resultado(self, resultado):
        self.card_resultados.pack(fill="x", padx=28, pady=8)
        for w in self.card_resultados.cuerpo.winfo_children():
            w.destroy()

        metricas = resultado.get("metricas", {}) or {}
        fila = ctk.CTkFrame(self.card_resultados.cuerpo, fg_color="transparent")
        fila.pack(fill="x", pady=6)

        kpis = [
            ("Registros Contables", metricas.get("registros_contables", "N/D")),
            ("Facturas Procesadas", metricas.get("facturas_pendientes", "N/D")),
            ("Llaves Conciliadas", metricas.get("llaves", "N/D")),
            ("Negocios Consolidados", metricas.get("negocios", "N/D")),
        ]

        for i, (tit, val) in enumerate(kpis):
            fila.grid_columnconfigure(i, weight=1)
            f = ctk.CTkFrame(fila, fg_color=COLORES["panel_suave"], corner_radius=8, padx=12, pady=10)
            f.grid(row=0, column=i, sticky="nsew", padx=4)
            ctk.CTkLabel(f, text=tit, text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(anchor="w")
            ctk.CTkLabel(f, text=str(val), text_color=COLORES["texto"], font=(FUENTE, 18, "bold")).pack(anchor="w")

    def _abrir_informe(self):
        if self.resultado_actual and self.resultado_actual.get("archivos_generados"):
            abrir_archivo_o_carpeta(self.resultado_actual["archivos_generados"][0])
