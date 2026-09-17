from pathlib import Path

from nucleo.contrato_proyecto import ContratoProyecto
from nucleo.resultados import ResultadoEjecucion
from nucleo.seguridad_salidas import bloquear_publicacion_corporativa


class AdaptadorInversiones(ContratoProyecto):
    def __init__(self, ruta_proyecto):
        self.ruta_proyecto = Path(ruta_proyecto)

    def obtener_metadatos(self):
        return {
            "id": "inversiones",
            "nombre": "Inversiones",
            "descripcion": "Procesamiento y conciliación de inversiones usando el motor original.",
            "estado": "DISPONIBLE",
        }

    def obtener_campos_configuracion(self):
        return [
            {
                "id": "periodo",
                "etiqueta": "Periodo (AAAA-MM)",
                "tipo": "periodo",
                "requerido": True,
            },
            {
                "id": "usuario_nacional",
                "etiqueta": "Usuario Nacional",
                "tipo": "texto",
                "requerido": True,
                "sensible": True,
            },
            {
                "id": "clave",
                "etiqueta": "Contraseña Nacional",
                "tipo": "password",
                "requerido": True,
                "sensible": True,
            },
            {
                "id": "publicar_corporativo",
                "etiqueta": "Publicar corporativamente",
                "tipo": "booleano",
                "requerido": False,
                "bloqueado": True,
            },
        ]

    def validar_disponibilidad(self):
        if not self.ruta_proyecto.exists() or not self.ruta_proyecto.is_dir():
            return {
                "disponible": False,
                "mensaje": f"No existe el proyecto de Inversiones: {self.ruta_proyecto}",
            }

        requeridos = [
            self.ruta_proyecto / "config.yaml",
            self.ruta_proyecto / "src" / "configuracion.py",
            self.ruta_proyecto / "src" / "insumos.py",
            self.ruta_proyecto / "src" / "insumos_red.py",
            self.ruta_proyecto / "src" / "proceso_inversiones.py",
        ]
        faltantes = [str(ruta) for ruta in requeridos if not ruta.exists()]
        if faltantes:
            return {
                "disponible": False,
                "mensaje": "Faltan componentes del motor: " + "; ".join(faltantes),
            }

        return {
            "disponible": True,
            "mensaje": "Motor de Inversiones disponible.",
        }

    def validar_parametros(self, parametros):
        errores = []
        periodo = str(parametros.get("periodo", "")).strip()
        usuario = str(parametros.get("usuario_nacional", "")).strip()
        clave = str(parametros.get("clave", ""))

        try:
            anio_texto, mes_texto = periodo.split("-")
            anio = int(anio_texto)
            mes = int(mes_texto)
            if len(anio_texto) != 4 or anio < 2000 or not 1 <= mes <= 12:
                raise ValueError
        except (ValueError, TypeError):
            errores.append("El periodo debe tener formato AAAA-MM y contener un mes válido.")

        if not usuario:
            errores.append("Ingrese el Usuario Nacional.")
        if not clave:
            errores.append("Ingrese la Contraseña Nacional.")

        try:
            bloquear_publicacion_corporativa(
                bool(parametros.get("publicar_corporativo", False))
            )
        except Exception as error:
            errores.append(str(error))

        return errores

    def ejecutar(self, parametros, reportar_evento):
        try:
            from integraciones.inversiones.proceso import ejecutar as ejecutar_inversiones

            anio_texto, mes_texto = str(parametros["periodo"]).strip().split("-")
            reportar_evento("INICIO", "Preparando ejecución de Inversiones.", 5)

            resultado = ejecutar_inversiones(
                anio=int(anio_texto),
                mes=int(mes_texto),
                usuario=str(parametros.get("usuario_nacional", "")).strip().upper(),
                clave=str(parametros.get("clave", "")),
                ruta_proyecto=str(self.ruta_proyecto),
                reportar_evento=reportar_evento,
            )

            return ResultadoEjecucion(
                exitoso=resultado.exitoso,
                estado="FINALIZADO",
                mensaje="Proceso de Inversiones ejecutado correctamente.",
                archivos_generados=[str(resultado.archivo_saldos)],
                carpeta_salida=str(Path(resultado.archivo_saldos).parent),
                metricas={
                    "periodo": resultado.periodo,
                    "cantidad_saldos": resultado.cantidad_saldos,
                    "cantidad_baseneg": resultado.cantidad_baseneg,
                    "total_mes": resultado.total_mes,
                },
            ).como_diccionario()

        except Exception as error:
            reportar_evento("ERROR", str(error), 100)
            return ResultadoEjecucion(
                exitoso=False,
                estado="ERROR",
                mensaje=str(error),
                errores=[str(error)],
            ).como_diccionario()
