# Databricks notebook source
# MAGIC %run ./_clientes_parameter

# COMMAND ----------

from pyspark.sql.functions import col, lit, to_date, current_timestamp 
from datetime import datetime, date
from pyspark.sql.functions import expr

# COMMAND ----------

dbutils.widgets.text('STR_INGESTION_DATE', '2025-05-01')

# COMMAND ----------

STR_INGESTION_DATE = dbutils.widgets.get("STR_INGESTION_DATE")
INGESTION_TIMESTAMP = datetime.strptime(STR_INGESTION_DATE, '%Y-%m-%d') if STR_INGESTION_DATE else datetime.now()

# COMMAND ----------

df_raw = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("cloudFiles.schemaLocation", SCHEMA_PATH)
    .option('header', True)
    .load(INPUT_PATH)
    # .withColumn('inserted_at', current_timestamp())
    .withColumn('inserted_at', lit(INGESTION_TIMESTAMP))
)

# COMMAND ----------

df_raw = df_raw.withColumn('fecha_nacimiento', expr('g0_catalog.default.encrypt_col(fecha_nacimiento)'))


# COMMAND ----------

(
    df_raw
    .writeStream
    .format('delta')
    .outputMode('append')
    .option('checkpointLocation', CHECKPOINT_PATH)
    .trigger(once=True)
    .table('g0_mkt_clientes.bronze.raw_clientes')
)