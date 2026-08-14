# Databricks notebook source
# MAGIC %md
# MAGIC ### Batch Layer: Procesa Datos Históricos

# COMMAND ----------

table_historical_tweets = 'g0_catalog.default.historical_tweets'
spark.sql(f'DROP TABLE IF EXISTS {table_historical_tweets}')

# COMMAND ----------

from pyspark.sql.functions import current_date, lit
from pyspark.sql.types import StructType, StructField, TimestampType, StringType

source_path = "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/tweets/"
fixed_date = "2025-05-05" 

schema = StructType([
    StructField("created_at", TimestampType(), True),
    StructField("current_comment", StringType(), True)
])

# Cargar tweets históricos (hasta ayer)
batch_df = (
    spark.read
    .option("header", "true")           # Si el CSV tiene encabezados
    .schema(schema)
    .csv(source_path)                   # Ruta al directorio o archivo CSV
    # .filter("created_at < current_date()")
    .filter(f"created_at < DATE('{fixed_date}')")
)

# Añadimos columna para identificar origen de los datos
batch_result = batch_df.withColumn("source", lit("batch"))

# Guardar el resultado en la tabla Delta
batch_result.write.format("delta").mode("overwrite").saveAsTable(table_historical_tweets)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM g0_catalog.default.historical_tweets

# COMMAND ----------

spark.sql(f'SELECT * FROM {table_historical_tweets}').display()