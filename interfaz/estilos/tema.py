from interfaz.estilos.colores import *


def obtener_estilos():

    return f"""
    
    QMainWindow {{
        background-color: {BACKGROUND};
    }}

    QWidget {{
        background-color: {BACKGROUND};
        color: {TEXT_PRIMARY};
        font-family: Segoe UI;
        font-size: 10pt;
    }}

    QPushButton {{
        background-color: {PRIMARY};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px;
    }}

    QPushButton:hover {{
        background-color: #1D4ED8;
    }}

    QFrame {{
        background: {CARD_BACKGROUND};
        border: 1px solid {BORDER};
        border-radius: 12px;
    }}
    """