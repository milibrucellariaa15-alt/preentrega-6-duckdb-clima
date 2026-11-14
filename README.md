# Pre-Entrega 6 - Análisis de Datos Meteorológicos con DuckDB y SQL

## Objetivo

El objetivo del proyecto es utilizar DuckDB como motor analítico para consultar y analizar directamente archivos CSV con datos meteorológicos, sin necesidad de utilizar una base de datos tradicional.

El análisis utiliza datos meteorológicos públicos de NOAA correspondientes al año 2025.

## Tecnologías utilizadas

- Python
- DuckDB
- SQL
- Pandas

## Fuente de datos

Los datos utilizados pertenecen al dataset Global Summary of the Day (GSOD) de NOAA.

Se utilizan seis archivos CSV correspondientes a seis estaciones meteorológicas diferentes. Los archivos son descargados automáticamente por el script y consultados directamente mediante DuckDB.

## Estructura del proyecto

```text
preentrega-6-duckdb-clima/
├── data/
│   └── archivos CSV meteorológicos
├── resultados/
│   ├── promedios_mensuales.csv
│   ├── maximos_por_estacion.csv
│   └── dias_extremos.csv
├── analisis_clima.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Instalación

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

Ejecutar:

```bash
python analisis_clima.py
```

El script:

1. Descarga los archivos meteorológicos.
2. Crea una conexión DuckDB en memoria.
3. Consulta directamente los archivos CSV.
4. Realiza un control de calidad.
5. Transforma los valores inválidos en NULL.
6. Convierte las temperaturas de Fahrenheit a Celsius.
7. Ejecuta tres consultas analíticas.
8. Exporta los resultados en formato CSV.

## Limpieza de datos

Se analizaron 1.131 registros correspondientes a 6 estaciones meteorológicas.

Durante el control de calidad se detectaron:

- 0 valores inválidos en TEMP.
- 4 valores inválidos en MAX.
- 2 valores inválidos en MIN.

Los valores inválidos se transformaron en NULL para evitar que alteraran los cálculos estadísticos. Los archivos originales no fueron modificados.

## Consultas realizadas

### 1. Promedios mensuales

Se calcularon por estación y mes:

- Temperatura media.
- Temperatura máxima promedio.
- Temperatura mínima promedio.
- Cantidad de observaciones válidas.

### 2. Máximos y mínimos por estación

Se calcularon las temperaturas máximas y mínimas de cada estación.

Entre los resultados obtenidos:

- Temperatura máxima: 30,61 °C en SKIBOTN 2.
- Temperatura mínima: -27,11 °C en EDGEOYA.

### 3. Días con temperaturas extremas

Se identificaron registros donde:

- La temperatura máxima fue igual o superior a 20 °C, o
- La temperatura mínima fue igual o inferior a -20 °C.

Se encontraron 80 días extremos.

## Tiempos de ejecución

Durante la ejecución realizada en Google Colab:

- Promedios mensuales: 0,3450 segundos.
- Máximos por estación: 0,5021 segundos.
- Días extremos: 0,3829 segundos.

Los tiempos pueden variar ligeramente según el entorno de ejecución.

## Resultados

Los resultados se exportan automáticamente a:

- `resultados/promedios_mensuales.csv`
- `resultados/maximos_por_estacion.csv`
- `resultados/dias_extremos.csv`

## Conclusión

DuckDB permitió consultar directamente múltiples archivos CSV mediante SQL sin necesidad de crear una base de datos tradicional.

El análisis integró datos de seis estaciones meteorológicas y permitió realizar limpieza, agregaciones, conteos y filtrados mediante SQL.

El uso de DuckDB como motor embebido permitió mantener un flujo simple, ligero y reproducible.
