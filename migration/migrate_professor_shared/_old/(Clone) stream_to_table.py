# Databricks notebook source
CATALOG = 'gx_catalog'

# COMMAND ----------

checkpoint_clientes_csv = "abfss://datalake@stdemdsai.dfs.core.windows.net/_checkpoints/g0/clientes_csv"
table_clientes_csv = f'{CATALOG}.default.clientes_csv'
spark.sql(f'DROP TABLE IF EXISTS {table_clientes_csv}')

# COMMAND ----------

dbutils.fs.rm(checkpoint_clientes_csv, recurse=True)

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql.functions import input_file_name

# Define the schema
schema = StructType([
    StructField("id", StringType(), True),
    StructField("nombre", StringType(), True),
    StructField("apellido", StringType(), True),
    StructField("edad", StringType(), True),
])


# Ruta de origen (raw files)
source_path = "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/clientes/"

# Leer stream desde archivos CSV
df_stream = (
    spark.readStream
    .format("csv")
    .option("header", "true")
    .schema(schema)
    .load(source_path)
)

# (Opcional) Agregar columna de trazabilidad
df_stream = df_stream.withColumn("source_file", input_file_name())

# Escribir como tabla Delta gestionada por Unity Catalog
query = (
    df_stream.writeStream
    .format("delta")
    .option("checkpointLocation", checkpoint_clientes_csv)
    .outputMode("append")
    .toTable(table_clientes_csv)
)


# COMMAND ----------

df_clientes_csv = spark.sql(f'SELECT * FROM {table_clientes_csv}')
df_clientes_csv.display()