FUENTE = "Segoe UI"

TEMAS = {
    "claro": {
        "fondo": "#F6F8FC",
        "panel": "#FFFFFF",
        "panel_suave": "#F8FAFC",
        "primario": "#2563EB",
        "primario_hover": "#1D4ED8",
        "primario_suave": "#EFF6FF",
        "texto": "#172033",
        "texto_secundario": "#667085",
        "borde": "#E4E7EC",
        "verde": "#15803D",
        "verde_suave": "#ECFDF3",
        "amarillo": "#B45309",
        "rojo": "#B91C1C",
        "violeta": "#6D28D9",
        "consola": "#101828",
        "consola_texto": "#E4E7EC",
    },
    "oscuro": {
        "fondo": "#111827",
        "panel": "#1F2937",
        "panel_suave": "#273449",
        "primario": "#60A5FA",
        "primario_hover": "#3B82F6",
        "primario_suave": "#1E3A5F",
        "texto": "#F3F4F6",
        "texto_secundario": "#AEB8C8",
        "borde": "#374151",
        "verde": "#34D399",
        "verde_suave": "#123D32",
        "amarillo": "#FBBF24",
        "rojo": "#F87171",
        "violeta": "#A78BFA",
        "consola": "#0B1220",
        "consola_texto": "#E5E7EB",
    },
}

COLORES = dict(TEMAS["claro"])


def aplicar_tema(nombre):
    nombre = nombre if nombre in TEMAS else "claro"
    COLORES.clear()
    COLORES.update(TEMAS[nombre])
    return nombre
