import customtkinter as ctk

FUENTE = "Segoe UI"

COLORES = {
    "fondo": ("#F5F5F2", "#0D0F10"),
    "panel": ("#FFFFFF", "#181B1E"),
    "panel_suave": ("#F1F2F0", "#222629"),
    "texto": ("#111111", "#F7F7F5"),
    "texto_secundario": ("#646A73", "#ADB4BC"),
    "borde": ("#E0E2E4", "#31363B"),
    "verde": ("#168A4A", "#35C77B"),
    "verde_suave": ("#E1F6E9", "#153A29"),
    "amarillo": ("#9F6A00", "#FFD65A"),
    "amarillo_suave": ("#FFF4C7", "#433817"),
    "rojo": ("#C9362A", "#FF7268"),
    "rojo_suave": ("#FBE4E1", "#43211F"),
    "azul": ("#245B95", "#69B4FA"),
    "azul_suave": ("#EAF3FD", "#153147"),
    "violeta": ("#6D45B8", "#BA9AFF"),
    "consola": ("#111315", "#07090A"),
    "consola_texto": ("#E7ECEF", "#E7ECEF"),
    "primario": ("#FFD522", "#FFD522"),
    "primario_hover": ("#F0C800", "#E8C000"),
    "sidebar": ("#181818", "#111315"),
    "sidebar_hover": ("#2A2A2A", "#292D30"),
}


def aplicar_tema(nombre):
    ctk.set_appearance_mode("light" if nombre == "claro" else "dark")
    return nombre
