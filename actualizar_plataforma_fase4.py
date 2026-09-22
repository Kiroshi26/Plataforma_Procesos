
"""Actualiza Plataforma_Procesos Fase 3 a Fase 4.

Ejecutar desde C:\\Proyectos\\Plataforma_Procesos con:
    python actualizar_plataforma_fase4.py
"""
from pathlib import Path
import json
import py_compile
import shutil
from datetime import datetime

BASE = Path(__file__).resolve().parent
if BASE.name.lower() != "plataforma_procesos":
    BASE = Path(r"C:\Proyectos\Plataforma_Procesos")

ADAPTADOR = BASE / "integraciones" / "comisiones" / "adaptador.py"
INTERFAZ = BASE / "interfaz" / "ventana_principal.py"
CONFIG = BASE / "configuracion" / "plataforma.json"

for ruta in (ADAPTADOR, INTERFAZ, CONFIG):
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró: {ruta}")

marca = datetime.now().strftime("%Y%m%d_%H%M%S")
respaldo = BASE / f"respaldo_fase3_{marca}"
(respaldo / "integraciones" / "comisiones").mkdir(parents=True, exist_ok=True)
(respaldo / "interfaz").mkdir(parents=True, exist_ok=True)
(respaldo / "configuracion").mkdir(parents=True, exist_ok=True)
shutil.copy2(ADAPTADOR, respaldo / "integraciones" / "comisiones" / "adaptador.py")
shutil.copy2(INTERFAZ, respaldo / "interfaz" / "ventana_principal.py")
shutil.copy2(CONFIG, respaldo / "configuracion" / "plataforma.json")

s = ADAPTADOR.read_text(encoding="utf-8")
old = '''        estado_motor = "REVISAR" if re.search(r"Estado general:\\s*REVISAR", texto_salida, re.I) else "OK"
        advertencias = []
'''
new = '''        estado_motor = "REVISAR" if re.search(r"Estado general:\\s*REVISAR", texto_salida, re.I) else "OK"

        def extraer_entero_salida(etiquetas):
            for etiqueta in etiquetas:
                coincidencia = re.search(
                    rf"(?im)^\\s*{re.escape(etiqueta)}\\s*:\\s*([0-9][0-9.,]*)",
                    texto_salida,
                )
                if coincidencia:
                    texto = coincidencia.group(1).replace(".", "").replace(",", "")
                    try:
                        return int(texto)
                    except ValueError:
                        return None
            return None

        metricas = {
            "anio": anio,
            "mes": mes,
            "periodo": f"{anio}-{mes:02d}",
            "estado_motor": estado_motor,
            "registros_contables": extraer_entero_salida([
                "Filas Qry_Cta250115", "Registros contables"
            ]),
            "facturas_pendientes": extraer_entero_salida([
                "Facturas pendientes", "Facturas procesadas"
            ]),
            "llaves": extraer_entero_salida([
                "Llaves conciliadas", "Llaves procesadas"
            ]),
            "negocios": extraer_entero_salida([
                "Negocios consolidados", "Negocios procesados"
            ]),
            "informe_origen": str(informe.resolve()),
        }

        advertencias = []
'''
if old not in s:
    raise RuntimeError("La versión del adaptador no corresponde a Fase 3.")
s = s.replace(old, new, 1)
old = '''            metricas={
                "anio": anio,
                "mes": mes,
                "estado_motor": estado_motor,
                "informe_origen": str(informe.resolve()),
            },
'''
if old not in s:
    raise RuntimeError("No se encontró el bloque de métricas anterior.")
s = s.replace(old, "            metricas=metricas,\n", 1)
ADAPTADOR.write_text(s, encoding="utf-8")

s = INTERFAZ.read_text(encoding="utf-8")
s = s.replace(
    "        self.en_ejecucion = False\n\n        self.title",
    "        self.en_ejecucion = False\n        self.ultimo_resultado = None\n\n        self.title",
    1,
)
s = s.replace(
    '''        self.consola.pack(fill="both", expand=True, padx=30, pady=(12, 24))
        self._escribir_consola("Módulo cargado. No se ha ejecutado ningún motor.")
''',
    '''        self.consola.pack(fill="both", expand=True, padx=30, pady=(12, 8))
        self.panel_resultado = tk.Frame(
            self.panel_principal,
            bg="#F8FAFC",
            highlightbackground=COLORES["borde"],
            highlightthickness=1,
        )
        self.panel_resultado.pack(fill="x", padx=30, pady=(0, 24))
        tk.Label(
            self.panel_resultado,
            text="El resumen de la última ejecución aparecerá aquí.",
            bg="#F8FAFC",
            fg=COLORES["texto_secundario"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=14, pady=12)
        self._escribir_consola("Módulo cargado. No se ha ejecutado ningún motor.")
''',
    1,
)
s = s.replace(
    "        self.proyecto_actual = self.registro.obtener(identificador)\n",
    "        self.proyecto_actual = self.registro.obtener(identificador)\n        self.ultimo_resultado = None\n",
    1,
)
s = s.replace(
    '''        archivos = resultado.get("archivos_generados", [])
''',
    '''        self._mostrar_resumen_resultado(resultado)
        archivos = resultado.get("archivos_generados", [])
''',
    1,
)
metodo = '''    def _mostrar_resumen_resultado(self, resultado):
        if not hasattr(self, "panel_resultado"):
            return
        for elemento in self.panel_resultado.winfo_children():
            elemento.destroy()

        estado = str(resultado.get("estado", "SIN ESTADO"))
        color = COLORES["verde"] if resultado.get("exitoso") else COLORES["amarillo"]
        if estado == "ERROR":
            color = COLORES["rojo"]

        cabecera = tk.Frame(self.panel_resultado, bg="#F8FAFC")
        cabecera.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(
            cabecera, text="RESUMEN DE LA EJECUCIÓN", bg="#F8FAFC",
            fg=COLORES["texto_secundario"], font=("Segoe UI", 9, "bold"),
        ).pack(side="left")
        tk.Label(
            cabecera, text=estado, bg="#F8FAFC", fg=color,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right")

        metricas = resultado.get("metricas", {}) or {}
        filas = [
            ("Periodo", metricas.get("periodo")),
            ("Estado del motor", metricas.get("estado_motor")),
            ("Registros contables", metricas.get("registros_contables")),
            ("Facturas pendientes", metricas.get("facturas_pendientes")),
            ("Llaves procesadas", metricas.get("llaves")),
            ("Negocios consolidados", metricas.get("negocios")),
        ]
        disponibles = [(nombre, valor) for nombre, valor in filas if valor is not None]
        if disponibles:
            rejilla = tk.Frame(self.panel_resultado, bg="#F8FAFC")
            rejilla.pack(fill="x", padx=10, pady=(2, 8))
            for indice, (nombre, valor) in enumerate(disponibles):
                tarjeta = tk.Frame(
                    rejilla, bg="white", highlightbackground=COLORES["borde"],
                    highlightthickness=1,
                )
                tarjeta.grid(row=indice // 3, column=indice % 3, sticky="nsew", padx=4, pady=4)
                tk.Label(
                    tarjeta, text=nombre, bg="white", fg=COLORES["texto_secundario"],
                    font=("Segoe UI", 8),
                ).pack(anchor="w", padx=10, pady=(8, 2))
                tk.Label(
                    tarjeta, text=str(valor), bg="white", fg=COLORES["texto"],
                    font=("Segoe UI", 11, "bold"),
                ).pack(anchor="w", padx=10, pady=(0, 8))
            for columna in range(3):
                rejilla.grid_columnconfigure(columna, weight=1)

        archivos = resultado.get("archivos_generados", [])
        if archivos:
            tk.Label(
                self.panel_resultado, text=f"Informe: {archivos[0]}",
                wraplength=760, justify="left", bg="#F8FAFC",
                fg=COLORES["azul"], font=("Segoe UI", 8),
            ).pack(anchor="w", padx=14, pady=(0, 12))

'''
needle = "    def _abrir_ultimo_archivo(self):\n"
if needle not in s:
    raise RuntimeError("No se encontró el punto de inserción de la interfaz.")
s = s.replace(needle, metodo + needle, 1)
INTERFAZ.write_text(s, encoding="utf-8")

config = json.loads(CONFIG.read_text(encoding="utf-8"))
config["version"] = "0.4.0"
CONFIG.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

try:
    py_compile.compile(str(ADAPTADOR), doraise=True)
    py_compile.compile(str(INTERFAZ), doraise=True)
except Exception:
    shutil.copy2(respaldo / "integraciones" / "comisiones" / "adaptador.py", ADAPTADOR)
    shutil.copy2(respaldo / "interfaz" / "ventana_principal.py", INTERFAZ)
    shutil.copy2(respaldo / "configuracion" / "plataforma.json", CONFIG)
    raise

print("=" * 72)
print("Plataforma actualizada correctamente a la versión 0.4.0")
print(f"Respaldo: {respaldo}")
print("=" * 72)
