import customtkinter as ctk

FUENTE = "Segoe UI"

COLORES = {
    "fondo": ("#F6F8FC", "#111827"),
    "panel": ("#FFFFFF", "#1F2937"),
    "panel_suave": ("#F8FAFC", "#273449"),
    "texto": ("#172033", "#F3F4F6"),
    "texto_secundario": ("#667085", "#AEB8C8"),
    "borde": ("#E4E7EC", "#374151"),
    "verde": ("#15803D", "#34D399"),
    "amarillo": ("#B45309", "#FBBF24"),
    "rojo": ("#B91C1C", "#F87171"),
    "violeta": ("#6D28D9", "#A78BFA"),
    "consola": ("#101828", "#0B1220"),
    "consola_texto": ("#E4E7EC", "#E5E7EB"),
    "primario": ("#2563EB", "#60A5FA"),
    "primario_hover": ("#1D4ED8", "#3B82F6"),
}

def aplicar_tema(nombre):
    modo = "light" if nombre == "claro" else "dark"
    ctk.set_appearance_mode(modo)
    ctk.set_default_color_theme("blue")
    return nombre
