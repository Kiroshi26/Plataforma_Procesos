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

PERIODOS_DISPONIBLES = [
    "01_ENE", "02_FEB", "03_MAR", "04_ABR",
    "05_MAY", "06_JUN", "07_JUL", "08_AGO",
    "09_SEP", "10_OCT", "11_NOV", "12_DIC",
]


class VistaCruceEfectivo(ctk.CTkFrame):
    """Vista moderna especializada para el Cruce de Efectivo y lectura de extractos PDF."""

    def __init__(self, parent, modulo, on_ejecutar, on_consola):
        super().__init__(parent, fg_color="transparent")
        self.modulo = modulo
        self.on_ejecutar = on_ejecutar
        self.on_consola = on_consola

        self.var_criterio = ctk.StringVar(value="FID")
        self.var_modo_masivo = ctk.BooleanVar(value=False)
        self.var_anio = ctk.StringVar(value=str(datetime.now().year))
        self.var_periodo = ctk.StringVar(value="01_ENE")
        self.var_archivo_ctasbanc = ctk.StringVar()
        self.var_carpeta_salida = ctk.StringVar(value=r"C:\Proyectos\pruebas\Salida_Cruce_Efectivo")

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
            text="📑",
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
            text="Cruce de Efectivo",
            text_color=COLORES["texto"],
            font=(FUENTE, 24, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            titulos,
            text="Búsqueda y lectura masiva de extractos PDF fiduciarios y cruce con cuentas bancarias.",
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 13),
        ).pack(anchor="w", pady=(2, 0))

        BadgePill(fila_top, "EXTRACCIÓN PDF", "verde").pack(side="right", padx=6)

        # 1. Criterio y Periodo
        card_busqueda = TarjetaSeccion(self, "1. Criterio de Búsqueda y Periodo", "Filtro del extracto (sufijo/negocio) y período a consultar.")

        fila_c = ctk.CTkFrame(card_busqueda.cuerpo, fg_color="transparent")
        fila_c.pack(fill="x", pady=4)

        ctk.CTkLabel(fila_c, text="Criterio:", text_color=COLORES["texto"], font=(FUENTE, 13, "bold")).pack(side="left", padx=(0, 8))
        self.entry_criterio = ctk.CTkEntry(
            fila_c,
            textvariable=self.var_criterio,
            width=130,
            placeholder_text="Ej. FID o código",
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
        )
        self.entry_criterio.pack(side="left", padx=(0, 20))

        ctk.CTkCheckBox(
            fila_c,
            text="Procesamiento Masivo (todos los criterios)",
            variable=self.var_modo_masivo,
            command=self._toggle_modo_masivo,
            font=(FUENTE, 12),
            text_color=COLORES["texto"],
            fg_color=COLORES["primario"],
            check_mark_color=COLORES["texto_boton"],
        ).pack(side="left", padx=(0, 20))

        fila_t = ctk.CTkFrame(card_busqueda.cuerpo, fg_color="transparent")
        fila_t.pack(fill="x", pady=(8, 4))

        ctk.CTkLabel(fila_t, text="Año:", text_color=COLORES["texto"], font=(FUENTE, 13, "bold")).pack(side="left", padx=(0, 8))
        self.entry_anio = ctk.CTkEntry(fila_t, textvariable=self.var_anio, width=90, fg_color=COLORES["panel_suave"], text_color=COLORES["texto"])
        self.entry_anio.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(fila_t, text="Periodo / Carpeta:", text_color=COLORES["texto"], font=(FUENTE, 13, "bold")).pack(side="left", padx=(0, 8))
        self.menu_periodo = ctk.CTkOptionMenu(
            fila_t,
            variable=self.var_periodo,
            values=PERIODOS_DISPONIBLES,
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
            button_color=COLORES["primario"],
            button_hover_color=COLORES["primario_hover"],
            dropdown_text_color=COLORES["texto"],
            width=130,
        )
        self.menu_periodo.pack(side="left")

        # 2. Maestro de Cuentas Bancarias
        card_cuentas = TarjetaSeccion(self, "2. Archivo Maestro de Cuentas Bancarias", "Opcional. Permite homologar tipo de cuenta, entidad y moneda contra el extracto.")
        fila_m = ctk.CTkFrame(card_cuentas.cuerpo, fg_color="transparent")
        fila_m.pack(fill="x", pady=4)

        self.entry_cuentas = ctk.CTkEntry(
            fila_m,
            textvariable=self.var_archivo_ctasbanc,
            placeholder_text="Seleccione el archivo Excel de cuentas bancarias (opcional)...",
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
        )
        self.entry_cuentas.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            fila_m,
            text="Examinar...",
            command=self._seleccionar_archivo_cuentas,
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
            hover_color=COLORES["borde"],
            font=(FUENTE, 12),
            width=100,
        ).pack(side="left")

        self.frame_columnas = ctk.CTkFrame(card_cuentas.cuerpo, fg_color="transparent")
        self.frame_columnas.pack(fill="x", pady=(6, 0))

        # 3. Carpeta de Salida
        card_salida = TarjetaSeccion(self, "3. Carpeta Local de Salida", "Destino donde se generará el consolidado Excel.")
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

        # 4. Panel de Ejecución
        card_accion = TarjetaSeccion(self, "4. Ejecución del Proceso", "Escanea los extractos PDF, extrae los saldos finales y compila el informe Excel.")

        fila_btn = ctk.CTkFrame(card_accion.cuerpo, fg_color="transparent")
        fila_btn.pack(fill="x", pady=4)

        self.btn_ejecutar = ctk.CTkButton(
            fila_btn,
            text="▶  Ejecutar Cruce de Efectivo",
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
            text="📊  Abrir Consolidado Excel",
            command=self._abrir_informe,
            state="disabled",
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
            hover_color=COLORES["borde"],
            font=(FUENTE, 13, "bold"),
            height=40,
        )
        self.btn_abrir_resultado.pack(side="left")

        self.progreso = ctk.CTkProgressBar(
            card_accion.cuerpo,
            mode="determinate",
            progress_color=COLORES["verde"],
            height=10,
        )
        self.progreso.set(0)
        self.progreso.pack(fill="x", pady=(14, 6))

        self.lbl_estado = ctk.CTkLabel(
            card_accion.cuerpo,
            text="Listo para buscar extractos.",
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 12),
        )
        self.lbl_estado.pack(anchor="w")

        # 5. Resumen de Resultados
        self.card_resultados = TarjetaSeccion(self, "5. Resumen de Extracción", "Detalles del informe generado.")
        self.card_resultados.pack_forget()

    def _toggle_modo_masivo(self):
        if self.var_modo_masivo.get():
            self.entry_criterio.configure(state="disabled")
        else:
            self.entry_criterio.configure(state="normal")

    def _seleccionar_archivo_cuentas(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de cuentas bancarias",
            filetypes=[("Archivos Excel", "*.xlsx *.xlsm *.xls"), ("Todos los archivos", "*.*")],
        )
        if ruta:
            self.var_archivo_ctasbanc.set(ruta)
            self._inspeccionar_columnas(Path(ruta))

    def _inspeccionar_columnas(self, ruta: Path):
        for w in self.frame_columnas.winfo_children():
            w.destroy()

        columnas_esperadas = ["CUENTA CONTABLE", "DESCRIPCION", "NOMBRE ENTIDAD", "MONEDA"]
        fila = ctk.CTkFrame(self.frame_columnas, fg_color="transparent")
        fila.pack(fill="x")

        def tarea():
            try:
                import pandas as pd
                df = pd.read_excel(ruta, nrows=2)
                cols = {str(c).strip().upper() for c in df.columns}
                self.after(0, lambda: self._mostrar_pills_cols(fila, columnas_esperadas, cols))
            except Exception as e:
                self.after(0, lambda: ctk.CTkLabel(fila, text=f"Error al leer columnas: {e}", text_color=COLORES["rojo"], font=(FUENTE, 11)).pack(anchor="w"))

        threading.Thread(target=tarea, daemon=True).start()

    def _mostrar_pills_cols(self, parent, esperadas, presentes):
        for col in esperadas:
            ok = col in presentes
            BadgePill(
                parent,
                f"✓ {col}" if ok else f"✗ {col}",
                "verde" if ok else "rojo",
            ).pack(side="left", padx=3, pady=2)

    def _seleccionar_carpeta_salida(self):
        ruta = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if ruta:
            self.var_carpeta_salida.set(ruta)

    def recoger_parametros(self):
        return {
            "criterio": self.var_criterio.get().strip(),
            "modo_masivo": self.var_modo_masivo.get(),
            "anio": self.var_anio.get().strip(),
            "periodo": self.var_periodo.get().strip(),
            "archivo_ctasbanc": self.var_archivo_ctasbanc.get().strip(),
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
        self.lbl_estado.configure(text="Buscando extractos PDF...")
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
            self.lbl_estado.configure(text="¡Cruce de Efectivo generado con éxito!")
            self._mostrar_resumen(resultado)
        else:
            self.lbl_estado.configure(text=resultado.get("mensaje", "Proceso finalizado."))

    def _mostrar_resumen(self, resultado):
        self.card_resultados.pack(fill="x", padx=28, pady=8)
        for w in self.card_resultados.cuerpo.winfo_children():
            w.destroy()

        metricas = resultado.get("metricas", {}) or {}
        fila = ctk.CTkFrame(self.card_resultados.cuerpo, fg_color="transparent")
        fila.pack(fill="x", pady=6)

        kpis = [
            ("Criterio Ejecutado", metricas.get("criterio", "N/D")),
            ("Periodo", metricas.get("periodo", "N/D")),
            ("Archivos Generados", metricas.get("total_archivos", "0")),
            ("Archivo Principal", metricas.get("archivo_principal", "N/D")),
        ]

        for i, (tit, val) in enumerate(kpis):
            fila.grid_columnconfigure(i, weight=1)
            f = ctk.CTkFrame(fila, fg_color=COLORES["panel_suave"], corner_radius=8, padx=12, pady=10)
            f.grid(row=0, column=i, sticky="nsew", padx=4)
            ctk.CTkLabel(f, text=tit, text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(anchor="w")
            ctk.CTkLabel(f, text=str(val), text_color=COLORES["texto"], font=(FUENTE, 14, "bold"), wraplength=160).pack(anchor="w")

    def _abrir_informe(self):
        if self.resultado_actual and self.resultado_actual.get("archivos_generados"):
            abrir_archivo_o_carpeta(self.resultado_actual["archivos_generados"][0])
