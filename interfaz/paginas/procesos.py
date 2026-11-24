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
            text="Selecciona un módulo corporativo para configurar y ejecutar.",
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
            text="Catálogo de procesos disponibles",
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

        ctk.CTkLabel(
            encabezado,
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

        ctk.CTkLabel(
            titulo_estado,
            text=meta.get("nombre", meta["id"]),
            text_color=COLORES["texto"],
            font=(FUENTE, 17, "bold"),
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
