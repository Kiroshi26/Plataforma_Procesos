import customtkinter as ctk

FUENTE = "Segoe UI"

COLORES = {
    # Paleta primaria Bancolombia
    "negro_cib": "#2C2A29",
    "blanco": "#FFFFFF",
    
    # Paleta secundaria Bancolombia
    "amarillo": "#FDDA24",
    "verde_andino": "#00C389",
    "violeta": "#9063CD",
    "naranja": "#FF7F41",
    "rosa": "#F5B6CD",
    "azul": "#59CBE8",

    # Colores lógicos de la interfaz (Adaptables Claro/Oscuro)
    "fondo": ("#F9F9F9", "#1E1E1E"),
    "panel": ("#FFFFFF", "#2C2A29"),
    "panel_suave": ("#F0F0F0", "#3A3837"),
    "texto": ("#2C2A29", "#FFFFFF"),
    "texto_secundario": ("#666666", "#A0A0A0"),
    "borde": ("#E0E0E0", "#4A4847"),
    
    # Estados
    "verde": ("#00C389", "#00C389"),
    "amarillo_estado": ("#FFB300", "#FFB300"),
    "rojo": ("#D32F2F", "#EF5350"), # Rojo estándar para errores
    "consola": ("#2C2A29", "#121212"),
    "consola_texto": ("#FFFFFF", "#E0E0E0"),
    
    # Botones primarios (Amarillo Macondo)
    "primario": ("#FDDA24", "#FDDA24"),
    "primario_hover": ("#E5C520", "#E5C520"),
    "texto_boton": ("#2C2A29", "#2C2A29"), # El texto sobre el amarillo siempre debe ser oscuro
}

def aplicar_tema(nombre):
    modo = "light" if nombre == "claro" else "dark"
    ctk.set_appearance_mode(modo)
    ctk.set_default_color_theme("blue")
    return nombre
