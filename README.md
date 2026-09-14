# Plataforma de Procesos

Fase 3 del aplicativo modular para Comisiones, Inversiones y futuros proyectos.

## Alcance actual

- Interfaz de escritorio modular.
- Comisiones conectado al motor real mediante un proceso independiente.
- Validación del año y mes seleccionado contra la configuración del proyecto.
- Consola visual con la salida real del motor.
- Ejecución en segundo plano.
- Copia del informe a una carpeta local seleccionada.
- Botón para abrir el informe generado.
- Estado `REVISAR` tratado como advertencia informativa.
- Inversiones continúa visible en modo local protegido, sin ejecución ni publicación corporativa.

## Instalar actualización

Descomprima el paquete directamente en `C:\Proyectos` y reemplace la carpeta
`Plataforma_Procesos`. No reemplace `Proyecto_Comisiones` ni `Proyecto_Inversiones`.

## Ejecutar

```powershell
cd "C:\Proyectos\Plataforma_Procesos"
python app.py
```

## Pruebas

```powershell
python -m unittest discover -s pruebas -v
```

## Comisiones

El adaptador utiliza preferentemente el Python ubicado en
`Proyecto_Comisiones\.venv\Scripts\python.exe`. El informe se genera primero por
el motor estable y luego se copia a la carpeta local elegida en la plataforma.

## Inversiones

La publicación corporativa permanece bloqueada hasta aprobación explícita.
