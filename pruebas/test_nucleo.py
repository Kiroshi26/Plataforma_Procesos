import tempfile
import unittest
from pathlib import Path

from nucleo.registro_proyectos import RegistroProyectos
from nucleo.seguridad_salidas import (
    ErrorSeguridadSalida,
    bloquear_publicacion_corporativa,
    validar_salida_local,
)


class PruebasNucleo(unittest.TestCase):
    def test_salida_local(self):
        with tempfile.TemporaryDirectory() as carpeta:
            self.assertTrue(validar_salida_local(carpeta).exists())

    def test_publicacion_inversiones_bloqueada(self):
        with self.assertRaises(ErrorSeguridadSalida):
            bloquear_publicacion_corporativa(True)

    def test_registro_vacio(self):
        self.assertEqual(RegistroProyectos().listar(), [])


if __name__ == "__main__":
    unittest.main()
