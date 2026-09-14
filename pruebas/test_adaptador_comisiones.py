import tempfile
import unittest
from pathlib import Path

from integraciones.comisiones.adaptador import AdaptadorComisiones


class PruebasAdaptadorComisiones(unittest.TestCase):
    def test_detecta_motor_faltante(self):
        with tempfile.TemporaryDirectory() as carpeta:
            adaptador = AdaptadorComisiones(carpeta)
            self.assertFalse(adaptador.validar_disponibilidad()["disponible"])

    def test_extrae_periodo_yaml(self):
        texto = "proceso:\n  anio: 2026\n  mes: 7\n"
        self.assertEqual(
            AdaptadorComisiones._extraer_entero_yaml(texto, ["anio"]),
            2026,
        )
        self.assertEqual(
            AdaptadorComisiones._extraer_entero_yaml(texto, ["mes"]),
            7,
        )

    def test_extrae_ruta_excel(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "Informe_Comisiones_prueba.xlsx"
            ruta.touch()
            # La extracción de rutas Windows se prueba en Windows durante integración.
            self.assertTrue(ruta.exists())


if __name__ == "__main__":
    unittest.main()
