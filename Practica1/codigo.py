# -*- coding: utf-8 -*-
"""
02_explorar_capas.py
====================
Script de exploración y diagnóstico de capas vectoriales (Shapefile).

Para cada capa definida:
    - Verifica su existencia y la de sus archivos complementarios (.shx, .dbf).
    - La carga con GeoPandas.
    - Imprime su estructura: registros, columnas, tipos, CRS, geometrías,
      extensión espacial, validez y las primeras cinco filas.
    - Registra cualquier error sin detener el procesamiento de las demás capas.

Al final consolida el diagnóstico en un DataFrame, lo imprime en pantalla
y lo guarda como CSV (UTF-8).

Uso (terminal de Windows):
    python 02_explorar_capas.py
    python 02_explorar_capas.py "C:\\otra\\carpeta\\de\\datos"   (opcional)
"""

# ---------------------------------------------------------------------------
# Importación de bibliotecas
# ---------------------------------------------------------------------------
import sys                      # Para leer un argumento opcional de la terminal
from pathlib import Path        # Manejo de rutas independiente del sistema

import geopandas as gpd         # Lectura y análisis de datos vectoriales
import pandas as pd             # Manejo de tablas (DataFrame del diagnóstico)


# ---------------------------------------------------------------------------
# CONFIGURACIÓN (modifique estas variables según su equipo)
# ---------------------------------------------------------------------------

# Carpeta raíz de la práctica
CARPETA_PROYECTO = Path(
    r"C:\Users\ricar\OneDrive\Desktop\MAESTRIA\SEMESTRE3"
    r"\programacion de SIG (Dra. Lidia)\practica1"
)

# Carpeta donde se encuentran los Shapefiles
CARPETA_DATOS = CARPETA_PROYECTO / "app_qgis"

# Lista de capas a revisar. Agregue aquí todos los archivos que tenga.
CAPAS = [
    "cuencas_limite.shp",
    "uso_suelo_limite.shp",
    "temperatura_limite.shp",
    "rios_limite.shp",
    "precipitacion_limite.shp",
    "climas_limite.shp",
    "carreteras_limite.shp",
]

# Si es True, además de la lista anterior se agregan automáticamente
# todos los .shp que existan en CARPETA_DATOS.
BUSCAR_TODOS_LOS_SHP = False

# Archivo CSV de salida con el diagnóstico consolidado
RUTA_CSV = CARPETA_PROYECTO / "generado con IA" / "01_diagnostico_capas.csv"

# Archivos complementarios obligatorios de un Shapefile
EXTENSIONES_OBLIGATORIAS = [".shx", ".dbf"]


# ---------------------------------------------------------------------------
# Excepción personalizada para capas vacías
# ---------------------------------------------------------------------------
class CapaVaciaError(Exception):
    """Se lanza cuando una capa no tiene registros o no tiene geometrías."""


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------
def configurar_pandas():
    """Ajusta la visualización de pandas para tablas anchas en la terminal."""
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 40)


def imprimir_titulo(texto, caracter="="):
    """Imprime un título enmarcado para separar secciones."""
    linea = caracter * 80
    print(f"\n{linea}\n{texto}\n{linea}")


def obtener_lista_capas(carpeta):
    """
    Devuelve la lista de rutas (Path) de las capas a procesar.
    Combina la lista CAPAS con los .shp detectados si BUSCAR_TODOS_LOS_SHP=True.
    """
    rutas = [carpeta / nombre for nombre in CAPAS]

    if BUSCAR_TODOS_LOS_SHP and carpeta.exists():
        # Se agregan los .shp de la carpeta que no estén ya en la lista
        existentes = {r.name.lower() for r in rutas}
        for shp in sorted(carpeta.glob("*.shp")):
            if shp.name.lower() not in existentes:
                rutas.append(shp)

    return rutas


def verificar_archivo(ruta):
    """
    Verifica que el .shp exista y que tenga sus archivos complementarios.
    Lanza FileNotFoundError si falta el .shp o algún complementario.
    Devuelve una advertencia (texto) si falta el .prj.
    """
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    # Revisa .shx y .dbf; sin ellos el Shapefile se considera dañado/incompleto
    faltantes = [ext for ext in EXTENSIONES_OBLIGATORIAS
                 if not ruta.with_suffix(ext).exists()]
    if faltantes:
        raise FileNotFoundError(
            f"Shapefile incompleto, faltan: {', '.join(faltantes)}"
        )

    # El .prj no es obligatorio, pero sin él no hay CRS
    if not ruta.with_suffix(".prj").exists():
        return "Sin archivo .prj (CRS no definido)"
    return ""


def clasificar_error(error):
    """
    Traduce una excepción a una categoría legible para el diagnóstico.
    GeoPandas puede usar pyogrio o fiona como motor, por lo que las
    excepciones se clasifican por su nombre y mensaje.
    """
    if isinstance(error, FileNotFoundError):
        return "Archivo inexistente"
    if isinstance(error, CapaVaciaError):
        return "Capa vacía o sin geometrías"

    nombre = type(error).__name__
    mensaje = str(error).lower()
    palabras_danado = ["corrupt", "not recognized", "unable to open",
                       "failed to open", "invalid", "unsupported",
                       "not a", "truncated", "bad"]

    # Errores típicos de pyogrio (DataSourceError) o fiona (DriverError)
    if nombre in ("DataSourceError", "DriverError") or \
            any(p in mensaje for p in palabras_danado):
        return "Archivo dañado"
    return "Error de lectura"


def diagnostico_vacio(ruta):
    """Crea el diccionario base del diagnóstico con valores por defecto."""
    return {
        "archivo": ruta.name,
        "ruta": str(ruta),
        "estado": "Pendiente",
        "tipo_error": "",
        "mensaje": "",
        "n_registros": None,
        "n_columnas": None,
        "columnas": "",
        "crs": "",
        "epsg": None,
        "tipos_geometria": "",
        "xmin": None,
        "ymin": None,
        "xmax": None,
        "ymax": None,
        "geom_nulas": None,
        "geom_vacias": None,
        "geom_validas": None,
        "geom_invalidas": None,
    }


# ---------------------------------------------------------------------------
# Funciones de análisis
# ---------------------------------------------------------------------------
def cargar_capa(ruta):
    """
    Lee la capa con GeoPandas y valida que tenga registros y geometrías.
    Lanza CapaVaciaError si la capa está vacía.
    """
    gdf = gpd.read_file(ruta)

    if len(gdf) == 0:
        raise CapaVaciaError("La capa no contiene registros.")
    if gdf.geometry.isna().all() or gdf.geometry.is_empty.all():
        raise CapaVaciaError("La capa no contiene geometrías válidas "
                             "(todas son nulas o vacías).")
    return gdf


def analizar_capa(gdf, diag):
    """
    Calcula las estadísticas descriptivas de la capa y las guarda en 'diag'.
    """
    geom = gdf.geometry

    # --- Estructura de la tabla ---
    diag["n_registros"] = len(gdf)
    diag["n_columnas"] = len(gdf.columns)
    diag["columnas"] = "; ".join(map(str, gdf.columns))

    # --- Sistema de referencia de coordenadas ---
    if gdf.crs is not None:
        diag["crs"] = gdf.crs.name
        diag["epsg"] = gdf.crs.to_epsg()
    else:
        diag["crs"] = "No definido"

    # --- Tipos de geometría (excluyendo nulas) ---
    tipos = geom.geom_type.dropna().value_counts()
    diag["tipos_geometria"] = "; ".join(f"{t} ({n})" for t, n in tipos.items())

    # --- Extensión espacial ---
    xmin, ymin, xmax, ymax = gdf.total_bounds
    diag.update({"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax})

    # --- Calidad de geometrías ---
    nulas = geom.isna()
    vacias = (~nulas) & geom.is_empty
    evaluables = (~nulas) & (~vacias)
    validas = geom[evaluables].is_valid

    diag["geom_nulas"] = int(nulas.sum())
    diag["geom_vacias"] = int(vacias.sum())
    diag["geom_validas"] = int(validas.sum())
    diag["geom_invalidas"] = int((~validas).sum())

    return diag


def imprimir_detalle(gdf, diag):
    """Imprime en pantalla el detalle completo de una capa leída."""
    print(f"Número de registros : {diag['n_registros']}")
    print(f"Número de columnas  : {diag['n_columnas']}")
    print(f"Nombres de columnas : {list(gdf.columns)}")

    print("\nTipos de datos de las columnas:")
    for columna, tipo in gdf.dtypes.items():
        print(f"   - {columna:<25} {tipo}")

    epsg = f" (EPSG:{diag['epsg']})" if diag["epsg"] else ""
    print(f"\nCRS                 : {diag['crs']}{epsg}")
    print(f"Tipo(s) de geometría: {diag['tipos_geometria']}")

    print("\nExtensión espacial:")
    print(f"   xmin = {diag['xmin']:.4f}   ymin = {diag['ymin']:.4f}")
    print(f"   xmax = {diag['xmax']:.4f}   ymax = {diag['ymax']:.4f}")

    print("\nCalidad de geometrías:")
    print(f"   Nulas     : {diag['geom_nulas']}")
    print(f"   Vacías    : {diag['geom_vacias']}")
    print(f"   Válidas   : {diag['geom_validas']}")
    print(f"   Inválidas : {diag['geom_invalidas']}")

    # Se muestran los atributos sin la columna de geometría (es muy larga)
    print("\nPrimeras 5 filas de la tabla de atributos:")
    atributos = pd.DataFrame(gdf.drop(columns=gdf.geometry.name))
    if atributos.shape[1] == 0:
        print("   (La capa no tiene atributos además de la geometría)")
    else:
        print(atributos.head(5).to_string())


def procesar_capa(ruta):
    """
    Procesa una sola capa: verifica, carga, analiza e imprime.
    Cualquier error se captura y se registra; nunca detiene el script.
    Devuelve el diccionario de diagnóstico.
    """
    diag = diagnostico_vacio(ruta)
    imprimir_titulo(f"CAPA: {ruta.name}")
    print(f"Ruta completa       : {ruta}")

    try:
        # 1) Verificación de existencia
        advertencia = verificar_archivo(ruta)

        # 2) Lectura
        gdf = cargar_capa(ruta)

        # 3) Análisis
        analizar_capa(gdf, diag)
        diag["estado"] = "Correcto"
        diag["mensaje"] = advertencia
        print("Estado de lectura   : CORRECTO")
        if advertencia:
            print(f"Advertencia         : {advertencia}")

        # 4) Impresión del detalle
        imprimir_detalle(gdf, diag)

    except FileNotFoundError as e:
        registrar_error(diag, e)
    except CapaVaciaError as e:
        registrar_error(diag, e)
    except Exception as e:  # Archivo dañado u otro error de lectura
        registrar_error(diag, e)

    return diag


def registrar_error(diag, error):
    """Guarda la información del error en el diagnóstico y la imprime."""
    diag["estado"] = "Error"
    diag["tipo_error"] = clasificar_error(error)
    diag["mensaje"] = f"{type(error).__name__}: {error}"
    print(f"Estado de lectura   : ERROR ({diag['tipo_error']})")
    print(f"Detalle             : {diag['mensaje']}")


# ---------------------------------------------------------------------------
# Funciones de consolidación y salida
# ---------------------------------------------------------------------------
def consolidar_diagnostico(lista_diagnosticos):
    """Convierte la lista de diccionarios en un DataFrame."""
    return pd.DataFrame(lista_diagnosticos)


def imprimir_resumen(df):
    """Imprime una tabla resumida con las columnas más relevantes."""
    imprimir_titulo("RESUMEN CONSOLIDADO DEL DIAGNÓSTICO")
    columnas = ["archivo", "estado", "tipo_error", "n_registros",
                "n_columnas", "epsg", "tipos_geometria",
                "geom_nulas", "geom_validas", "geom_invalidas"]
    print(df[columnas].to_string(index=False))


def guardar_csv(df, ruta_csv):
    """
    Guarda el diagnóstico en CSV (UTF-8 con BOM para que Excel muestre
    correctamente acentos y la letra ñ). Crea la carpeta si no existe.
    Devuelve True si se guardó correctamente.
    """
    try:
        ruta_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(ruta_csv, index=False, encoding="utf-8-sig")
        return True
    except PermissionError:
        print(f"\nERROR: no se pudo escribir {ruta_csv}. "
              "¿Está abierto en Excel?")
    except OSError as e:
        print(f"\nERROR al guardar el CSV: {e}")
    return False


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------
def main():
    """Ejecuta el flujo completo de exploración de capas."""
    configurar_pandas()

    # Permite indicar otra carpeta de datos desde la terminal (opcional)
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else CARPETA_DATOS

    imprimir_titulo("EXPLORACIÓN DE CAPAS VECTORIALES")
    print(f"Carpeta de datos: {carpeta}")
    if not carpeta.exists():
        print("ADVERTENCIA: la carpeta de datos no existe; "
              "todas las capas se reportarán como inexistentes.")

    # Procesamiento de cada capa (un error no detiene a las demás)
    rutas = obtener_lista_capas(carpeta)
    diagnosticos = [procesar_capa(ruta) for ruta in rutas]

    # Consolidación, impresión y guardado
    df = consolidar_diagnostico(diagnosticos)
    imprimir_resumen(df)
    guardado = guardar_csv(df, RUTA_CSV)

    # Resumen final
    total = len(df)
    correctas = int((df["estado"] == "Correcto").sum())
    errores = total - correctas

    imprimir_titulo("RESULTADO FINAL")
    print(f"Capas definidas             : {total}")
    print(f"Capas procesadas con éxito  : {correctas}")
    print(f"Capas con errores           : {errores}")
    if guardado:
        print(f"Archivo CSV generado        : {RUTA_CSV}")
    else:
        print("Archivo CSV generado        : (no se pudo guardar)")


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()