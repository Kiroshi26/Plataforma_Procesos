import unittest

from app import cargar_configuracion, crear_registro


class PruebasConfiguracionInterfaz(unittest.TestCase):
    def test_registra_ambos_proyectos(self):
        registro = crear_registro(cargar_configuracion())
        ids = {item["id"] for item in registro.listar()}
        self.assertEqual(ids, {"comisiones", "inversiones"})

    def test_publicacion_inversiones_desautorizada(self):
        configuracion = cargar_configuracion()
        self.assertFalse(
            configuracion["seguridad"][
                "inversiones_publicacion_corporativa_autorizada"
            ]
        )


if __name__ == "__main__":
    unittest.main()
