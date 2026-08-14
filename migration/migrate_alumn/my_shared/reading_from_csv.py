# Databricks notebook source
# MAGIC %sql
# MAGIC SELECT * FROM read_files(
# MAGIC   'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/clientes/clientes_20250501.csv',
# MAGIC   format => 'csv',
# MAGIC   header => true,
# MAGIC   inferSchema => true,
# MAGIC   mode => 'FAILFAST'
# MAGIC )

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM read_files(
# MAGIC   'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/archivo_subido_20250517.txt',
# MAGIC   format => 'text',
# MAGIC   header => true,
# MAGIC   inferSchema => true,
# MAGIC   mode => 'FAILFAST'
# MAGIC )

# COMMAND ----------

from pyspark.sql.functions import current_date, lit
from pyspark.sql.types import StructType, StructField, TimestampType, StringType

source_path = "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/"

schema = StructType([
    StructField("value", StringType(), True)
])

df_airflow = (
    spark.read
    .option("header", "true")           # Si el CSV tiene encabezados
    .schema(schema)
    .text(source_path)                   # Ruta al directorio o archivo CSV
)

# batch_result.write.format("delta").mode("overwrite").saveAsTable("my_catalog.my_schema.historical_tweets")
df_airflow.display()