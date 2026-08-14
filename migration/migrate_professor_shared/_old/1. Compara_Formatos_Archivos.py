# Databricks notebook source
#%pip install apache-iceberg[spark]==1.9.2
#%pip install apache-iceberg[spark]==0.13.1

# COMMAND ----------

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.demo_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.demo_catalog.type", "hadoop") \
    .config("spark.sql.catalog.demo_catalog.warehouse", "/tmp/iceberg_warehouse") \
    .getOrCreate()


# COMMAND ----------

    print(spark.version)

# COMMAND ----------

# MAGIC %md
# MAGIC # Laboratorio de Comparación de Formatos de Archivo en Big Data
# MAGIC **Objetivo:** Ilustrar la importancia de seleccionar el formato de archivo correcto mediante la comparación de CSV, Avro, Parquet, Delta Lake e Iceberg.
# MAGIC
# MAGIC **Métricas:**
# MAGIC  1.  **Peso del Archivo:** Tamaño en disco.
# MAGIC  2.  **Tiempo de Escritura:** Latencia en operaciones de guardado.
# MAGIC  3.  **Tiempo de Lectura y Consulta:** Latencia en operaciones de análisis.

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP VOLUME IF EXISTS workspace.default.testfiles;
# MAGIC CREATE VOLUME workspace.default.testfiles;

# COMMAND ----------

import time
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count

# Definir rutas para almacenar los datos
base_path = "/Volumes/workspace/default/testfiles"

dbutils.fs.rm(base_path, recurse=True) # Limpiar ejecuciones anteriores
dbutils.fs.mkdirs(base_path)

# Rutas específicas para cada formato
paths = {
    "csv": f"{base_path}/csv",
    "avro": f"{base_path}/avro",
    "parquet": f"{base_path}/parquet",
    "delta": f"{base_path}/delta",
    "iceberg_table": "workspace.default.taxis_iceberg" # Usando el catálogo configurado
}

# DataFrame para almacenar los resultados de las métricas
results = []

print("Entorno y rutas configuradas.")


# COMMAND ----------

display(dbutils.fs.ls("/Volumes/workspace/default/testfiles"))



# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 1: Carga del Conjunto de Datos de Origen
# MAGIC
# MAGIC Usaremos el conjunto de datos de taxis de Nueva York, que está disponible públicamente en Databricks. Este conjunto de datos es lo suficientemente grande como para mostrar diferencias de rendimiento significativas.
# MAGIC
# MAGIC Dataset con 6135075 registros.
# MAGIC

# COMMAND ----------

# Cargar el dataset de origen en un DataFrame de Spark
# Usamos una muestra para que el laboratorio se ejecute rápidamente. 
# Para una prueba más exhaustiva, puedes usar el dataset completo.
source_df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("/databricks-datasets/nyctaxi/tripdata/yellow/yellow_tripdata_2019-01.csv.gz") \
    .sample(fraction=0.8, seed=42) # Usamos una muestra del 80%

# Cachear el DataFrame para acelerar las operaciones subsiguientes
source_df.localCheckpoint()
print(f"Dataset de origen cargado con {source_df.count()} registros.")
source_df.printSchema()


# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2: Ingesta y Transformación
# MAGIC
# MAGIC Para cada formato, realizaremos dos operaciones:
# MAGIC 1.  **Escritura Inicial:** Escribir el DataFrame de origen directamente.
# MAGIC 2.  **Transformación y Escritura:** Aplicar una transformación simple (filtrado y agregación) y guardar el resultado.
# MAGIC

# COMMAND ----------

#display(spark.sql("DESCRIBE EXTENDED taxis_iceberg"))

# COMMAND ----------

def run_experiment_for_format(format_name, df):
    """
    Ejecuta el ciclo de escritura, lectura y consulta para un formato específico.
    """
    path = paths.get(format_name)
    iceberg_table_name = paths.get("iceberg_table")
    df_schema=df.schema

    print(" --- 1. Escritura Inicial ---")
    start_time = time.time()
    if format_name == "iceberg":        
        #df.write.format("iceberg").mode("overwrite").save(iceberg_table_name)
       df.createOrReplaceTempView("temp_df")
       spark.sql(f"CREATE TABLE IF NOT EXISTS {iceberg_table_name} USING iceberg AS SELECT * FROM temp_df")
    else:
        df.write.format(format_name).mode("overwrite").save(path)
    write_time = time.time() - start_time
    
    print("--- 2. Medición del Tamaño del Archivo ---")
    if format_name == "iceberg":
        # Para Iceberg, el tamaño se calcula sobre el directorio del warehouse
        #file_size_bytes = sum([f.size for f in dbutils.fs.ls(f"{spark.conf.get('spark.sql.catalog.workspace.default')}/{iceberg_table_name.split('.')[2]}") if f.size > 0])
        catalog_name = "default"
        file_size_bytes = sum([f.size for f in dbutils.fs.ls(f"{catalog_name}/{iceberg_table_name.split('.')[2]}") if f.size > 0])
    else:
        file_size_bytes = sum([f.size for f in dbutils.fs.ls(path) if f.size > 0])
    file_size_mb = file_size_bytes / (1024 * 1024)

    print(" --- 3. Lectura de los datos ---")
    start_time = time.time()
    if format_name == "iceberg":
        read_df = spark.read.format("iceberg").load(iceberg_table_name)
    elif format_name == "csv":        
        read_df = spark.read.format(format_name).schema(df_schema).load(path)
    else:
        read_df = spark.read.format(format_name).load(path)
    # Forzar una acción para medir el tiempo de lectura real
    read_df.count()
    read_time = time.time() - start_time

    print(" --- 4. Consulta Analítica 1: Agregación simple ---")
    start_time = time.time()
    query1_result = read_df.groupBy("PULocationID").agg(avg("total_amount")).collect()
    query1_time = time.time() - start_time

    print(" --- 5. Consulta Analítica 2: Filtrado y conteo ---")
    start_time = time.time()
    query2_result = read_df.filter(col("passenger_count") > 2).count()
    query2_time = time.time() - start_time
    
    print(" Guardar resultados")
    results.append({
        "Formato": format_name.upper(),
        "Tamaño (MB)": file_size_mb,
        "Tiempo Escritura (s)": write_time,
        "Tiempo Lectura (s)": read_time,
        "Tiempo Consulta Agregación (s)": query1_time,
        "Tiempo Consulta Filtro (s)": query2_time
    })
    
    print(f"Experimento completado para el formato: {format_name.upper()}")


# COMMAND ----------

# MAGIC %md
# MAGIC ### Ejecutar el experimento para cada formato

# COMMAND ----------

# Ejecutar el experimento para cada formato
formats_to_test = ["avro", "parquet", "delta","csv"]
#formats_to_test = ["iceberg",]
for fmt in formats_to_test:
    print(formats_to_test)
    run_experiment_for_format(fmt, source_df)

# Liberar la caché
#if not spark.conf.get("spark.databricks.clusterUsageTags.clusterType") == "serverless":
  # source_df.unpersist()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 3: Análisis de Resultados y Visualización
# MAGIC
# MAGIC Ahora que hemos recopilado las métricas de rendimiento, vamos a consolidarlas en una tabla y a visualizarlas para facilitar la comparación.

# COMMAND ----------

# Crear un DataFrame de Pandas para una fácil visualización
results_df = pd.DataFrame(results)
display(results_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Visualización del Tamaño de Archivo
# MAGIC
# MAGIC Un menor tamaño de archivo no solo ahorra costos de almacenamiento, sino que también reduce la cantidad de I/O (Entrada/Salida) necesaria, lo que generalmente conduce a consultas más rápidas.
# MAGIC

# COMMAND ----------

# Usar la función display() de Databricks para generar gráficos interactivos
display(results_df.plot(kind='bar', x='Formato', y='Tamaño (MB)', 
                        title='Comparación de Tamaño de Archivo (Menor es mejor)',
                        color='skyblue', figsize=(10, 6)))


# COMMAND ----------

# MAGIC %md
# MAGIC **Observaciones (Tamaño):**
# MAGIC *   **CSV:** Es el formato menos eficiente en términos de espacio. Al ser basado en texto, no utiliza compresión avanzada ni codificaciones eficientes.
# MAGIC *   **AVRO:** Es un formato basado en filas y binario, lo que ofrece una mejor compresión que CSV.
# MAGIC *   **PARQUET, DELTA, ICEBERG:** Son formatos columnares. Almacenan los datos por columnas, lo que permite una compresión y codificación mucho más efectivas, resultando en archivos significativamente más pequeños. Delta e Iceberg se basan en Parquet, por lo que su tamaño es similar.
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Visualización de Tiempos de Escritura y Lectura
# MAGIC

# COMMAND ----------

display(results_df.plot(kind='bar', x='Formato', y=['Tiempo Escritura (s)', 'Tiempo Lectura (s)'], 
                        title='Comparación de Tiempos de I/O (Menor es mejor)',
                        figsize=(12, 7)))


# COMMAND ----------

# MAGIC %md
# MAGIC **Observaciones (I/O):**
# MAGIC *   **Escritura:** Los formatos como CSV pueden ser rápidos para escribir porque no requieren un procesamiento complejo. Delta e Iceberg tienen una sobrecarga adicional debido al registro de transacciones, lo que puede hacer que su escritura sea ligeramente más lenta que Parquet puro.
# MAGIC *   **Lectura:** Aquí es donde los formatos columnares brillan. Parquet, Delta e Iceberg son mucho más rápidos porque solo leen las columnas necesarias para la consulta, evitando leer datos innecesarios del disco.
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Visualización de Tiempos de Consulta Analítica
# MAGIC

# COMMAND ----------

display(results_df.plot(kind='bar', x='Formato', y=['Tiempo Consulta Agregación (s)', 'Tiempo Consulta Filtro (s)'], 
                        title='Comparación de Rendimiento de Consultas Analíticas (Menor es mejor)',
                        color=['coral', 'lightgreen'], figsize=(12, 7)))


# COMMAND ----------

# MAGIC %md
# MAGIC **Observaciones (Consultas):**
# MAGIC *   **CSV y AVRO:** Al ser formatos basados en filas, para ejecutar una consulta de agregación o filtro sobre columnas específicas, el motor debe leer filas completas, descartando la mayoría de los datos en memoria. Esto los hace muy ineficientes para cargas de trabajo analíticas.
# MAGIC *   **PARQUET, DELTA, ICEBERG:** Su naturaleza columnar es ideal para estas consultas. El motor de Spark puede leer únicamente los datos de las columnas `PULocationID`, `total_amount` y `passenger_count` sin tocar el resto del dataset. Esto, combinado con optimizaciones como *predicate pushdown*, resulta en una latencia drásticamente menor.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Tabla Comparativa
# MAGIC
# MAGIC | Característica          | CSV                               | Avro                              | Parquet                           |
# MAGIC |-------------------------|-----------------------------------|-----------------------------------|-----------------------------------|
# MAGIC | **Estructura**          | Basado en texto, sin esquema      | Basado en filas, con esquema JSON | Basado en columnas, con esquema   |
# MAGIC | **Evolución de Esquema**| Manual, propenso a errores        | Excelente soporte                 | Bueno (adición de columnas)       |
# MAGIC | **Tipos de Datos**      | Solo texto                        | Complejos y primitivos            | Complejos y anidados              |
# MAGIC | **Datos Anidados**      | No soportado                      | Soportado                         | Excelente soporte                 |
# MAGIC | **Compresión**          | No nativa (compresión de archivo) | Buena (Snappy, Deflate)           | Excelente (Snappy, Gzip, LZO)     |
# MAGIC | **Rendimiento Lectura** | Lento                             | Rápido (para filas completas)     | Muy rápido (para columnas selectas)|
# MAGIC | **Uso Ideal**           | Intercambio de datos simple       | Ingesta de datos (streaming)      | Data Warehousing, Analytics (OLAP)|
# MAGIC
# MAGIC ### Recomendación:
# MAGIC - **Parquet:** Es el formato preferido para Data Lakes y análisis de Big Data en Spark debido a su rendimiento y compresión.
# MAGIC - **Avro:** Ideal para la ingesta de datos y pipelines de streaming donde el esquema puede cambiar con frecuencia.
# MAGIC - **CSV:** Útil para exportar datos a sistemas heredados o para análisis rápidos y sencillos donde el rendimiento no es crítico.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusiones Finales
# MAGIC
# MAGIC Este laboratorio demuestra de forma práctica por qué la elección del formato de archivo es una de las decisiones más críticas en la arquitectura de un Data Lake o Lakehouse.
# MAGIC
# MAGIC 1.  **Para Cargas de Trabajo Analíticas, Evita CSV:** CSV es útil para la ingesta inicial o el intercambio de datos legible por humanos, pero es extremadamente ineficiente para el almacenamiento y el análisis a gran escala.
# MAGIC
# MAGIC 2.  **Los Formatos Columnares son el Estándar de Oro:** **Parquet** ofrece un rendimiento y una compresión excelentes para consultas analíticas. Es la base sobre la que se construyen los formatos de tabla modernos.
# MAGIC
# MAGIC 3.  **Delta Lake e Iceberg son el Futuro (y el Presente) del Lakehouse:** Ambos formatos heredan todos los beneficios de rendimiento de Parquet y añaden características cruciales para la gobernanza y la fiabilidad de los datos:
# MAGIC     *   **Transacciones ACID:** Garantizan la consistencia de los datos, eliminando los problemas de corrupción en escrituras concurrentes.
# MAGIC     *   **Time Travel (Versionado):** Permiten consultar versiones anteriores de los datos, lo que es invaluable para auditorías, depuración y recuperación de errores.
# MAGIC     *   **Evolución de Esquema Segura:** Permiten modificar la estructura de las tablas sin reescribir todo el conjunto de datos.
# MAGIC     *   **Operaciones DML (UPDATE, DELETE, MERGE):** Habilitan operaciones a nivel de fila, que son imposibles o muy ineficientes en Parquet o CSV puros.
# MAGIC
# MAGIC La elección entre **Delta Lake** (profundamente integrado en Databricks) e **Iceberg** (un estándar abierto con un ecosistema en rápido crecimiento) dependerá de las necesidades específicas de tu organización, pero ambos representan la evolución natural y necesaria más allá de los simples archivos Parquet.
# MAGIC