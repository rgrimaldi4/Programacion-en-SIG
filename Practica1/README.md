Practica 1. 
Generar codigo con IA con el siguiente promp:

Tengo ocho capas vectoriales en formato Shapefile almacenadas en la carpeta:

C:\Users\ricar\OneDrive\Desktop\MAESTRIA\SEMESTRE3\programacion de SIG (Dra. Lidia)\practica1\app_qgis

Los archivos son:

- cuencas_limite.shp
- uso_suelo_limite.shp
- temperatura_limite.shp
- rios_limite.shp
- precipitacion_limite.shp
- climas_limite.shp
- carreteras_limite.shp


Necesito un script en Python llamado 02_explorar_capas.py que utilice las bibliotecas GeoPandas, pandas y pathlib para realizar las siguientes actividades:

1. Definir la carpeta de los datos mediante una ruta configurable.
2. Verificar que cada archivo exista antes de intentar leerlo.
3. Cargar cada capa vectorial con GeoPandas.
4. Imprimir en pantalla, para cada capa:
   - Nombre del archivo.
   - Ruta completa.
   - Estado de lectura.
   - Número de registros.
   - Número y nombres de las columnas.
   - Tipos de datos de las columnas.
   - Sistema de referencia de coordenadas (CRS).
   - Tipo o tipos de geometría.
   - Extensión espacial: xmin, ymin, xmax y ymax.
   - Número de geometrías nulas.
   - Número de geometrías válidas e inválidas.
   - Las primeras cinco filas de la tabla de atributos.
5. Gestionar mediante try-except los siguientes problemas:
   - Archivo inexistente.
   - Archivo dañado.
   - Error de lectura.
   - Capa vacía o sin geometrías.
6. Continuar procesando las demás capas cuando una presente errores.
7. Consolidar el diagnóstico de todas las capas en un DataFrame.
8. Imprimir en pantalla una tabla con el resumen consolidado.
9. Guardar el diagnóstico en formato CSV con codificación UTF-8 en:

C:\Users\ricar\OneDrive\Desktop\MAESTRIA\SEMESTRE3\programacion de SIG (Dra. Lidia)\practica1\generado con IA\01_diagnostico_capas.csv

10. Al finalizar, imprimir:
    - Número total de capas definidas.
    - Número de capas procesadas correctamente.
    - Número de capas con errores.
    - Ruta del archivo CSV generado.

El código debe:

- Estar completamente comentado en español.
- Organizarse mediante funciones.
- Utilizar pathlib para administrar las rutas.
- Incluir una función principal main().
- Ejecutarse mediante if __name__ == "__main__".
- No detenerse si una de las capas no existe o presenta errores.
- Estar listo para ejecutarse desde la terminal de Windows con:

python 01_explorar_capas.py

Proporciona el código completo y una explicación breve de los archivos de salida.
