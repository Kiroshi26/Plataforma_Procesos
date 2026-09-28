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
    "fondo": ("#F5F7F9", "#111111"), # Light grey background as in mockup
    "panel": ("#FFFFFF", "#212121"), # White cards
    "panel_suave": ("#F0F3F7", "#2C2A29"), # Very light grey for some backgrounds
    "texto": ("#2C2A29", "#FFFFFF"),
    "texto_secundario": ("#666666", "#A0A0A0"),
    "borde": ("#E0E5EC", "#333333"),
    
    # Estados y Alertas
    "verde": ("#008A4D", "#008A4D"), # Darker green for text on pills
    "fondo_pill_verde": ("#E0F2E9", "#1C3326"), # Light green pill bg
    "amarillo_estado": ("#FDDA24", "#FDDA24"),
    "rojo": ("#D32F2F", "#EF5350"),
    "consola": ("#2C2A29", "#121212"),
    "consola_texto": ("#FFFFFF", "#E0E0E0"),
    
    # Sidebar
    "sidebar": ("#1E1E1E", "#000000"),
    "sidebar_texto": ("#E0E0E0", "#E0E0E0"),
    "sidebar_activo": ("#FDDA24", "#FDDA24"),
    "sidebar_texto_activo": ("#2C2A29", "#2C2A29"),
    
    # Botones primarios
    "primario": ("#FDDA24", "#FDDA24"),
    "primario_hover": ("#E5C520", "#E5C520"),
    "texto_boton": ("#2C2A29", "#2C2A29"), 
    
    # Iconos y tarjetas grises
    "fondo_icono_gris": ("#F2F4F7", "#333333"),
    "icono_gris": ("#666666", "#AAAAAA"),
    
    # Botones modulo claro
    "fondo_modulo": ("#FFF8D6", "#443311"), # Light yellow background for process icons
}

def aplicar_tema(nombre):
    modo = "light" if nombre == "claro" else "dark"
    ctk.set_appearance_mode(modo)
    ctk.set_default_color_theme("blue")
    return nombre
