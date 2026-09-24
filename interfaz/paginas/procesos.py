import customtkinter as ctk
from interfaz.estilos import FUENTE, COLORES


class PaginaProcesos(ctk.CTkScrollableFrame):
    def __init__(self, parent, registro, on_abrir_proceso):
        super().__init__(parent, fg_color="transparent")
        self.registro = registro
        self.on_abrir_proceso = on_abrir_proceso

        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.pack(fill="x", padx=25, pady=(26, 14))

        ctk.CTkLabel(
            cabecera,
            text="Procesos",
            text_color=COLORES["texto"],
            font=(FUENTE, 28, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            cabecera,
            text="Selecciona un módulo para configurar y ejecutar.",
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 14),
        ).pack(anchor="w", pady=(3, 0))

        panel = ctk.CTkFrame(
            self,
            fg_color=COLORES["panel"],
            corner_radius=12,
            border_width=1,
            border_color=COLORES["borde"],
        )
        panel.pack(fill="both", expand=True, padx=20, pady=(0, 22))

        ctk.CTkLabel(
            panel,
            text="Procesos disponibles",
            text_color=COLORES["texto"],
            font=(FUENTE, 18, "bold"),
        ).pack(anchor="w", padx=18, pady=(16, 2))

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

        for indice, meta in enumerate(registro.listar()):
            proyecto = registro.obtener(meta["id"])

            try:
                disponibilidad = proyecto.validar_disponibilidad()
            except Exception as error:
                disponibilidad = {
                    "disponible": False,
                    "mensaje": str(error),
                }

            card = self._crear_tarjeta(
                rejilla,
                meta,
                disponibilidad,
            )

            card.grid(
                row=indice // 2,
                column=indice % 2,
                sticky="nsew",
                padx=7,
                pady=7,
            )

    def _crear_tarjeta(self, parent, meta, disponibilidad):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORES["panel"],
            corner_radius=12,
            border_width=1,
            border_color=COLORES["borde"],
        )

        disponible = bool(
            disponibilidad.get("disponible")
        )

        color_estado = (
            COLORES["verde"]
            if disponible
            else COLORES["rojo"]
        )

        contenido = ctk.CTkFrame(
            card,
            fg_color="transparent",
        )
        contenido.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=16,
        )

        encabezado = ctk.CTkFrame(
            contenido,
            fg_color="transparent",
        )
        encabezado.pack(fill="x")

        icono = "▤"
        if meta.get("id") == "inversiones":
            icono = "▥"

        ctk.CTkLabel(
            encabezado,
            text=icono,
            width=58,
            height=58,
            corner_radius=10,
            fg_color=("#FFF2BC", "#423917"),
            text_color=COLORES["texto"],
            font=(FUENTE, 26, "bold"),
        ).pack(side="left", padx=(0, 14))

        titulo_estado = ctk.CTkFrame(
            encabezado,
            fg_color="transparent",
        )
        titulo_estado.pack(
            side="left",
            fill="x",
            expand=True,
        )

        ctk.CTkLabel(
            titulo_estado,
            text=meta.get("nombre", meta["id"]),
            text_color=COLORES["texto"],
            font=(FUENTE, 17, "bold"),
        ).pack(anchor="w")

        estado_texto = str(
            meta.get(
                "estado",
                "DISPONIBLE" if disponible else "NO DISPONIBLE",
            )
        ).upper()

        badge = ctk.CTkLabel(
            titulo_estado,
            text=estado_texto,
            height=26,
            corner_radius=8,
            fg_color=("#DDF5E7", "#153A29") if disponible else ("#FBE3E0", "#43211F"),
            text_color=color_estado,
            font=(FUENTE, 10, "bold"),
        )
        badge.pack(anchor="w", pady=(6, 0))

        ctk.CTkLabel(
            contenido,
            text=meta.get("descripcion", ""),
            wraplength=450,
            justify="left",
            text_color=COLORES["texto_secundario"],
            font=(FUENTE, 12),
        ).pack(
            anchor="w",
            pady=(14, 8),
        )

        mensaje = disponibilidad.get(
            "mensaje",
            "",
        )

        if mensaje:
            ctk.CTkLabel(
                contenido,
                text=mensaje,
                wraplength=450,
                justify="left",
                text_color=color_estado,
                font=(FUENTE, 11),
            ).pack(anchor="w", pady=(0, 10))

        ctk.CTkButton(
            contenido,
            text="Abrir módulo   →",
            fg_color=COLORES["primario"],
            text_color="#111111",
            hover_color=COLORES["primario_hover"],
            font=(FUENTE, 12, "bold"),
            corner_radius=7,
            command=lambda: self.on_abrir_proceso(
                meta["id"]
            ),
        ).pack(
            anchor="e",
            pady=(6, 0),
        )

        return card
