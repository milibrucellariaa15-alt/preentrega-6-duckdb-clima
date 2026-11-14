
import duckdb
import os
import urllib.request
import time


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

os.makedirs("data", exist_ok=True)
os.makedirs("resultados", exist_ok=True)

BASE_URL = "https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/2025/"

ARCHIVOS = [
    "01001099999.csv",
    "01001499999.csv",
    "01002099999.csv",
    "01003099999.csv",
    "01006099999.csv",
    "01037099999.csv"
]


# ============================================================
# 2. DESCARGA DE DATOS
# ============================================================

print("Descargando datos meteorológicos...")

for archivo in ARCHIVOS:

    url = BASE_URL + archivo
    destino = os.path.join("data", archivo)

    if not os.path.exists(destino):
        urllib.request.urlretrieve(url, destino)
        print(f"Descargado: {archivo}")
    else:
        print(f"Ya existe: {archivo}")


# ============================================================
# 3. CONEXIÓN CON DUCKDB
# ============================================================

con = duckdb.connect(database=":memory:")

print("\nConexión con DuckDB creada correctamente.")


# ============================================================
# 4. LECTURA DIRECTA DE LOS CSV
# ============================================================

con.execute("""
    CREATE OR REPLACE VIEW clima AS

    SELECT *
    FROM read_csv_auto(
        'data/*.csv',
        header=True
    )
""")


# ============================================================
# 5. CONTROL DE CALIDAD
# ============================================================

control_calidad = con.sql("""
    SELECT
        COUNT(*) AS registros_totales,
        COUNT(DISTINCT STATION) AS cantidad_estaciones,

        SUM(
            CASE
                WHEN TEMP IS NULL OR TEMP >= 9999
                THEN 1 ELSE 0
            END
        ) AS temp_invalidas,

        SUM(
            CASE
                WHEN MAX IS NULL OR MAX >= 9999
                THEN 1 ELSE 0
            END
        ) AS max_invalidas,

        SUM(
            CASE
                WHEN MIN IS NULL OR MIN >= 9999
                THEN 1 ELSE 0
            END
        ) AS min_invalidas

    FROM clima
""").df()

print("\nControl de calidad:")
print(control_calidad)


# ============================================================
# 6. LIMPIEZA Y TRANSFORMACIÓN
# ============================================================

con.execute("""
    CREATE OR REPLACE VIEW clima_limpio AS

    SELECT
        STATION,
        NAME,
        CAST(DATE AS DATE) AS fecha,

        CASE
            WHEN TEMP IS NULL OR TEMP >= 9999
            THEN NULL
            ELSE ROUND((TEMP - 32) * 5.0 / 9.0, 2)
        END AS temp_c,

        CASE
            WHEN MAX IS NULL OR MAX >= 9999
            THEN NULL
            ELSE ROUND((MAX - 32) * 5.0 / 9.0, 2)
        END AS max_c,

        CASE
            WHEN MIN IS NULL OR MIN >= 9999
            THEN NULL
            ELSE ROUND((MIN - 32) * 5.0 / 9.0, 2)
        END AS min_c,

        PRCP

    FROM clima
""")


# ============================================================
# 7. CONSULTA 1 - PROMEDIOS MENSUALES
# ============================================================

inicio = time.perf_counter()

promedios_mensuales = con.sql("""
    SELECT
        STATION,
        NAME,
        EXTRACT(MONTH FROM fecha) AS mes,
        ROUND(AVG(temp_c), 2) AS temperatura_media_c,
        ROUND(AVG(max_c), 2) AS maxima_promedio_c,
        ROUND(AVG(min_c), 2) AS minima_promedio_c,
        COUNT(temp_c) AS cantidad_registros

    FROM clima_limpio

    WHERE temp_c IS NOT NULL

    GROUP BY
        STATION,
        NAME,
        EXTRACT(MONTH FROM fecha)

    ORDER BY
        STATION,
        mes
""").df()

tiempo_promedios = time.perf_counter() - inicio


# ============================================================
# 8. CONSULTA 2 - MÁXIMOS POR ESTACIÓN
# ============================================================

inicio = time.perf_counter()

maximos_estacion = con.sql("""
    SELECT
        STATION,
        NAME,
        ROUND(MAX(max_c), 2) AS temperatura_maxima_c,
        ROUND(MIN(min_c), 2) AS temperatura_minima_c,
        COUNT(temp_c) AS dias_analizados

    FROM clima_limpio

    WHERE temp_c IS NOT NULL

    GROUP BY
        STATION,
        NAME

    ORDER BY
        temperatura_maxima_c DESC
""").df()

tiempo_maximos = time.perf_counter() - inicio


# ============================================================
# 9. CONSULTA 3 - TEMPERATURAS EXTREMAS
# ============================================================

inicio = time.perf_counter()

dias_extremos = con.sql("""
    SELECT
        STATION,
        NAME,
        fecha,
        temp_c,
        max_c,
        min_c

    FROM clima_limpio

    WHERE
        max_c IS NOT NULL
        AND min_c IS NOT NULL
        AND (
            max_c >= 20
            OR min_c <= -20
        )

    ORDER BY
        min_c ASC,
        max_c DESC
""").df()

tiempo_extremos = time.perf_counter() - inicio


# ============================================================
# 10. EXPORTACIÓN DE RESULTADOS
# ============================================================

promedios_mensuales.to_csv(
    "resultados/promedios_mensuales.csv",
    index=False
)

maximos_estacion.to_csv(
    "resultados/maximos_por_estacion.csv",
    index=False
)

dias_extremos.to_csv(
    "resultados/dias_extremos.csv",
    index=False
)


# ============================================================
# 11. RESUMEN
# ============================================================

print("\nAnálisis terminado correctamente.")

print("\nTiempos de ejecución:")
print(f"Promedios mensuales: {tiempo_promedios:.4f} segundos")
print(f"Máximos por estación: {tiempo_maximos:.4f} segundos")
print(f"Días extremos: {tiempo_extremos:.4f} segundos")

print(f"\nCantidad de días extremos: {len(dias_extremos)}")

print("\nResultados guardados en la carpeta 'resultados'.")

con.close()
