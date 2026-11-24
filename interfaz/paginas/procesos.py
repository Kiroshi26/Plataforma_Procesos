import customtkinter as ctk
from interfaz.estilos import COLORES, FUENTE


class PaginaProcesos(ctk.CTkScrollableFrame):
    def __init__(self, parent, registro, on_abrir_proceso):
        super().__init__(parent, fg_color="transparent")
        self.registro = registro
        self.on_abrir_proceso = on_abrir_proceso

        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.pack(fill="x", padx=28, pady=(24, 14))
        ctk.CTkLabel(
            cabecera,
            text="Procesos",
            text_color=COLORES["texto"],
            font=(FUENTE, 30, "bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            cabecera,
            text="Selecciona un módulo corporativo para configurar y ejecutar.",
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 14),
        ).pack(anchor="w", pady=(3, 0))
        
        procesos = self.registro.listar()

        disponibles = 0

        estados = {}

        if not hasattr(self.registro, "_cache_disponibilidad"):
         self.registro._cache_disponibilidad = {}

        for meta in procesos:

         identificador = meta["id"]

        if identificador not in self.registro._cache_disponibilidad:

         try:
            self.registro._cache_disponibilidad[
                identificador
            ] = self.registro.obtener(
                identificador
            ).validar_disponibilidad()

         except Exception as error:

            self.registro._cache_disponibilidad[
                identificador
            ] = {
                "disponible": False,
                "mensaje": str(error)
            }

        estado = self.registro._cache_disponibilidad[
         identificador
    ]

        estados[identificador] = estado

        disponibles += int(
        bool(
            estado.get("disponible")
        )
    )
        resumen = ctk.CTkFrame(self, fg_color="transparent")
        resumen.pack(fill="x", padx=22, pady=(0, 10))
        for col in range(3):
          resumen.grid_columnconfigure(col, weight=1, uniform="resumen")
        datos = [
            ("▦", "Registrados", len(procesos), "Módulos en AP", COLORES["azul_suave"], COLORES["azul"]),
            ("✓", "Disponibles", disponibles, "Listos para ejecutar", COLORES["verde_suave"], COLORES["verde"]),
            ("−", "No disponibles", len(procesos) - disponibles, "Requieren revisión", COLORES["panel_suave"], COLORES["texto_secundario"]),
        ]
        for i, dato in enumerate(datos):
            self._resumen(resumen, *dato).grid(row=0, column=i, sticky="nsew", padx=6, pady=4)

        panel = ctk.CTkFrame(
            self,
            fg_color=COLORES["panel"],
            corner_radius=14,
            border_width=1,
            border_color=COLORES["borde"],
        )
        panel.pack(fill="both", expand=True, padx=20, pady=(2, 22))
        ctk.CTkLabel(
            panel,
            text="Catálogo de procesos disponibles",
            text_color=COLORES["texto"],
            font=(FUENTE, 18, "bold"),
        ).pack(anchor="w", padx=18, pady=(16, 1))
        ctk.CTkLabel(
            panel,
            text="Módulos registrados actualmente en el Aplicativo de Procesos.",
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 12),
        ).pack(anchor="w", padx=18, pady=(0, 10))

        rejilla = ctk.CTkFrame(panel, fg_color="transparent")
        rejilla.pack(fill="both", expand=True, padx=10, pady=(0, 12))
        for columna in range(2):
            rejilla.grid_columnconfigure(columna, weight=1, uniform="procesos")

        for indice, meta in enumerate(procesos):
            card = self._crear_tarjeta(rejilla, meta, estados.get(meta["id"], {}))
            card.grid(row=indice // 2, column=indice % 2, sticky="nsew", padx=7, pady=7)

    def _resumen(self, parent, icono, titulo, valor, detalle, fondo, color):
        card = ctk.CTkFrame(parent, fg_color=COLORES["panel"], corner_radius=12, border_width=1, border_color=COLORES["borde"])
        ctk.CTkLabel(card, text=icono, width=44, height=44, corner_radius=9, fg_color=fondo, text_color=color, font=(FUENTE, 18, "bold")).pack(side="left", padx=(13, 9), pady=12)
        texto = ctk.CTkFrame(card, fg_color="transparent")
        texto.pack(side="left", fill="both", expand=True, pady=9)
        ctk.CTkLabel(texto, text=titulo, text_color=COLORES["texto_secundario"], font=(FUENTE, 10)).pack(anchor="w")
        ctk.CTkLabel(texto, text=str(valor), text_color=COLORES["texto"], font=(FUENTE, 20, "bold")).pack(anchor="w")
        ctk.CTkLabel(texto, text=detalle, text_color=COLORES["texto_secundario"], font=(FUENTE, 9)).pack(anchor="w")
        return card

    def _crear_tarjeta(self, parent, meta, disponibilidad):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORES["panel"],
            corner_radius=12,
            border_width=1,
            border_color=COLORES["borde"],
        )
        disponible = bool(disponibilidad.get("disponible"))
        color_estado = COLORES["verde"] if disponible else COLORES["rojo"]
        fondo_estado = COLORES["verde_suave"] if disponible else COLORES["rojo_suave"]

        disponible = bool(disponibilidad.get("disponible"))

        contenido = ctk.CTkFrame(card, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=16, pady=16)

        encabezado = ctk.CTkFrame(contenido, fg_color="transparent")
        encabezado.pack(fill="x")

        id_proc = meta.get("id", "").lower()
        if "comision" in id_proc:
            icono = "🪙"
        elif "cruce" in id_proc:
            icono = "📑"
        else:
            icono = "📊"

        icono = "▤" if meta.get("id") != "inversiones" else "▥"
        ctk.CTkLabel(
            superior,
            text=icono,
            width=58,
            height=58,
            corner_radius=10,
            fg_color=COLORES["fondo_modulo"],
            text_color=COLORES["texto"],
            font=(FUENTE, 26),
        ).pack(side="left", padx=(0, 14))

        titulo_estado = ctk.CTkFrame(encabezado, fg_color="transparent")
        titulo_estado.pack(side="left", fill="x", expand=True)

        info = ctk.CTkFrame(superior, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            info,
            text=meta.get("nombre", meta.get("id", "Proceso")),
            text_color=COLORES["texto"],
            font=(FUENTE, 18, "bold"),
        ).pack(anchor="w")

        badge = ctk.CTkLabel(
            titulo_estado,
            text="DISPONIBLE" if disponible else "NO DISPONIBLE",
            height=22,
            corner_radius=4,
            fg_color=COLORES["fondo_pill_verde"] if disponible else COLORES["fondo_pill_rojo"],
            text_color=COLORES["verde"] if disponible else COLORES["rojo"],
            font=(FUENTE, 10, "bold"),
            padx=8,
        )
        badge.pack(anchor="w", pady=(3, 0))

        ctk.CTkLabel(
            contenido,
            text=meta.get("descripcion", ""),
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 12),
            wraplength=340,
            justify="left",
        ).pack(anchor="w", pady=(12, 12), fill="x")

        detalle_disp = ctk.CTkLabel(
            contenido,
            text=f"• {disponibilidad.get('mensaje', '')}",
            text_color=COLORES["verde"] if disponible else COLORES["rojo"],
            font=(FUENTE, 11),
            wraplength=340,
            justify="left",
        )
        detalle_disp.pack(anchor="w", pady=(0, 14), fill="x")

        boton = ctk.CTkButton(
            contenido,
            text="Abrir módulo →",
            command=lambda: self.on_abrir_proceso(meta["id"]),
            fg_color=COLORES["primario"],
            hover_color=COLORES["primario_hover"],
            text_color=COLORES["texto_boton"],
            font=(FUENTE, 13, "bold"),
            height=34,
        )
        boton.pack(anchor="w")

        return card
