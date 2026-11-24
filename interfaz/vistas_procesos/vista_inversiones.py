# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
from interfaz.estilos import COLORES, FUENTE
from interfaz.vistas_procesos.vista_base import (
    BadgePill,
    TarjetaSeccion,
    abrir_archivo_o_carpeta,
)


class VistaInversiones(ctk.CTkFrame):
    """Vista moderna especializada para la Conciliación de Inversiones Fiduciarias."""

    def __init__(self, parent, modulo, on_ejecutar, on_consola):
        super().__init__(parent, fg_color="transparent")
        self.modulo = modulo
        self.on_ejecutar = on_ejecutar
        self.on_consola = on_consola

        self.var_periodo = ctk.StringVar(value="2025-12")
        self.var_usuario = ctk.StringVar()
        self.var_clave = ctk.StringVar()
        self.var_mostrar_clave = ctk.BooleanVar(value=False)
        self.var_modo = ctk.StringVar(value="produccion")

        self.resultado_actual = None
        self._construir_ui()
        self._verificar_insumos()

    def _construir_ui(self):
        # Cabecera moderna
        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.pack(fill="x", padx=28, pady=(24, 12))

        fila_top = ctk.CTkFrame(cabecera, fg_color="transparent")
        fila_top.pack(fill="x")

        icono = ctk.CTkLabel(
            fila_top,
            text="📊",
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
            text="Inversiones Fiduciarias",
            text_color=COLORES["texto"],
            font=(FUENTE, 24, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            titulos,
            text="Conciliación entre base de datos Óptima (Nacional), Formato 351 y Base de Negocios.",
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 13),
        ).pack(anchor="w", pady=(2, 0))

        BadgePill(fila_top, "CONCILIACIÓN FIDUCIARIA", "azul").pack(side="right", padx=6)

        # 1. Parámetros de Conexión y Periodo
        card_param = TarjetaSeccion(self, "1. Parámetros y Credenciales", "Periodo contable y acceso a base de datos Óptima (DSN NACIONALET01).")

        fila_p = ctk.CTkFrame(card_param.cuerpo, fg_color="transparent")
        fila_p.pack(fill="x", pady=4)

        ctk.CTkLabel(fila_p, text="Periodo (AAAA-MM):", text_color=COLORES["texto"], font=(FUENTE, 13, "bold")).pack(side="left", padx=(0, 8))
        self.entry_periodo = ctk.CTkEntry(fila_p, textvariable=self.var_periodo, width=110, fg_color=COLORES["panel_suave"], text_color=COLORES["texto"])
        self.entry_periodo.pack(side="left", padx=(0, 24))

        ctk.CTkLabel(fila_p, text="Usuario Nacional:", text_color=COLORES["texto"], font=(FUENTE, 13, "bold")).pack(side="left", padx=(0, 8))
        self.entry_usuario = ctk.CTkEntry(fila_p, textvariable=self.var_usuario, width=130, placeholder_text="USR_FIDU", fg_color=COLORES["panel_suave"], text_color=COLORES["texto"])
        self.entry_usuario.pack(side="left", padx=(0, 24))

        ctk.CTkLabel(fila_p, text="Contraseña:", text_color=COLORES["texto"], font=(FUENTE, 13, "bold")).pack(side="left", padx=(0, 8))
        self.entry_clave = ctk.CTkEntry(fila_p, textvariable=self.var_clave, show="*", width=130, fg_color=COLORES["panel_suave"], text_color=COLORES["texto"])
        self.entry_clave.pack(side="left", padx=(0, 8))

        self.btn_ver_clave = ctk.CTkButton(
            fila_p,
            text="👁",
            width=32,
            height=30,
            command=self._toggle_ver_clave,
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
            hover_color=COLORES["borde"],
        )
        self.btn_ver_clave.pack(side="left")

        # 2. Insumos del Motor
        card_insumos = TarjetaSeccion(self, "2. Verificación de Insumos Fiduciarios", "Archivos requeridos en la carpeta insumos del motor.")
        self.frame_insumos_status = ctk.CTkFrame(card_insumos.cuerpo, fg_color="transparent")
        self.frame_insumos_status.pack(fill="x", pady=4)

        # 3. Panel de Ejecución
        card_accion = TarjetaSeccion(self, "3. Ejecución del Proceso", "Consulta los saldos, genera las subcuentas y concilia contra Formato 351.")

        fila_btn = ctk.CTkFrame(card_accion.cuerpo, fg_color="transparent")
        fila_btn.pack(fill="x", pady=4)

        self.btn_ejecutar = ctk.CTkButton(
            fila_btn,
            text="▶  Ejecutar Conciliación de Inversiones",
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
            text="📊  Abrir Saldos_Inversiones.xlsx",
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
            text="Listo para conectar con Óptima.",
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 12),
        )
        self.lbl_estado.pack(anchor="w")

        # 4. Resultados Financieros
        self.card_kpis = TarjetaSeccion(self, "4. Resultados Financieros y Conciliación", "Métricas y resumen de descuadres detectados.")
        self.card_kpis.pack_forget()

    def _toggle_ver_clave(self):
        mostrar = not self.var_mostrar_clave.get()
        self.var_mostrar_clave.set(mostrar)
        self.entry_clave.configure(show="" if mostrar else "*")

    def _verificar_insumos(self):
        for w in self.frame_insumos_status.winfo_children():
            w.destroy()

        ruta_insumos = self.modulo.ruta_proyecto / "insumos"
        base_neg = ruta_insumos / "BASE_NEGOCIOS_FIDUCIARIOS.xlsx"
        f351_encontrado = list(ruta_insumos.glob("Formato351_Fiduciaria*.xlsx"))

        fila = ctk.CTkFrame(self.frame_insumos_status, fg_color="transparent")
        fila.pack(fill="x")

        # Badge Base Negocios
        tiene_bn = base_neg.exists()
        BadgePill(
            fila,
            "✓ BASE NEGOCIOS FIDUCIARIOS" if tiene_bn else "✗ Falta BASE_NEGOCIOS_FIDUCIARIOS.xlsx",
            "verde" if tiene_bn else "rojo",
        ).pack(side="left", padx=4)

        # Badge Formato 351
        tiene_f351 = len(f351_encontrado) > 0
        txt_f351 = f"✓ FORMATO 351 ({f351_encontrado[0].name})" if tiene_f351 else "✗ Falta Formato 351 Excel"
        BadgePill(
            fila,
            txt_f351,
            "verde" if tiene_f351 else "rojo",
        ).pack(side="left", padx=4)

        # Botón para abrir carpeta insumos
        ctk.CTkButton(
            fila,
            text="Abrir Carpeta Insumos",
            command=lambda: abrir_archivo_o_carpeta(str(ruta_insumos)),
            fg_color=COLORES["panel_suave"],
            text_color=COLORES["texto"],
            hover_color=COLORES["borde"],
            font=(FUENTE, 11),
            height=24,
        ).pack(side="right")

    def recoger_parametros(self):
        return {
            "periodo": self.var_periodo.get().strip(),
            "usuario_nacional": self.var_usuario.get().strip(),
            "clave": self.var_clave.get(),
            "publicar_corporativo": False,
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
        self.lbl_estado.configure(text="Conectando con base de datos Óptima...")
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
            self.lbl_estado.configure(text="¡Conciliación completada exitosamente!")
            self._mostrar_kpis_financieros(resultado)
        else:
            self.lbl_estado.configure(text=resultado.get("mensaje", "Proceso finalizado."))

    def _mostrar_kpis_financieros(self, resultado):
        self.card_kpis.pack(fill="x", padx=28, pady=8)
        for w in self.card_kpis.cuerpo.winfo_children():
            w.destroy()

        metricas = resultado.get("metricas", {}) or {}
        saldo_contable = float(metricas.get("total_saldo_contable", 0.0) or 0.0)
        saldo_f351 = float(metricas.get("total_saldo_f351", 0.0) or 0.0)
        diferencias = float(metricas.get("total_diferencias", 0.0) or 0.0)
        partidas_dif = int(metricas.get("registros_con_diferencia", 0) or 0)

        fila = ctk.CTkFrame(self.card_kpis.cuerpo, fg_color="transparent")
        fila.pack(fill="x", pady=6)
        for c in range(4):
            fila.grid_columnconfigure(c, weight=1)

        # Card 1: Saldo Contable
        f1 = ctk.CTkFrame(fila, fg_color=COLORES["panel_suave"], corner_radius=8, padx=14, pady=10)
        f1.grid(row=0, column=0, sticky="nsew", padx=4)
        ctk.CTkLabel(f1, text="Total Saldo Contable", text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(anchor="w")
        ctk.CTkLabel(f1, text=f"${saldo_contable:,.2f}", text_color=COLORES["texto"], font=(FUENTE, 16, "bold")).pack(anchor="w")

        # Card 2: Saldo F351
        f2 = ctk.CTkFrame(fila, fg_color=COLORES["panel_suave"], corner_radius=8, padx=14, pady=10)
        f2.grid(row=0, column=1, sticky="nsew", padx=4)
        ctk.CTkLabel(f2, text="Total Saldo Formato 351", text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(anchor="w")
        ctk.CTkLabel(f2, text=f"${saldo_f351:,.2f}", text_color=COLORES["texto"], font=(FUENTE, 16, "bold")).pack(anchor="w")

        # Card 3: Diferencia Total
        color_dif = COLORES["verde"] if abs(diferencias) < 0.01 else COLORES["rojo"]
        f3 = ctk.CTkFrame(fila, fg_color=COLORES["panel_suave"], corner_radius=8, padx=14, pady=10)
        f3.grid(row=0, column=2, sticky="nsew", padx=4)
        ctk.CTkLabel(f3, text="Diferencia Neta", text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(anchor="w")
        ctk.CTkLabel(f3, text=f"${diferencias:,.2f}", text_color=color_dif, font=(FUENTE, 16, "bold")).pack(anchor="w")

        # Card 4: Partidas con Diferencia
        f4 = ctk.CTkFrame(fila, fg_color=COLORES["panel_suave"], corner_radius=8, padx=14, pady=10)
        f4.grid(row=0, column=3, sticky="nsew", padx=4)
        ctk.CTkLabel(f4, text="Partidas con Descuadre", text_color=COLORES["texto_secundario"], font=(FUENTE, 11)).pack(anchor="w")
        ctk.CTkLabel(f4, text=str(partidas_dif), text_color=color_dif, font=(FUENTE, 16, "bold")).pack(anchor="w")

    def _abrir_informe(self):
        if self.resultado_actual and self.resultado_actual.get("archivos_generados"):
            abrir_archivo_o_carpeta(self.resultado_actual["archivos_generados"][0])
