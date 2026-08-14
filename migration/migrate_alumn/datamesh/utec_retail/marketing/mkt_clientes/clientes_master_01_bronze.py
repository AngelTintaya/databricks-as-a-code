# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook **will run** in Pipeline
# MAGIC - Need to create table BRONZE_TB_RAW_CLIENTES with databricks autoloader
# MAGIC - COMMENT widget creation: dbutils.widgets.text() -> It will be created in the pipeline

# COMMAND ----------

# MAGIC %run ./__clientes_parameter

# COMMAND ----------

from pyspark.sql.functions import col, lit, to_date, current_timestamp 
from datetime import datetime, date
from pyspark.sql.functions import expr

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dataproduct Parameters

# COMMAND ----------

dict_paths = get_paths()
SCHEMA_PATH = dict_paths.get('SCHEMA_PATH')
INPUT_PATH = dict_paths.get('INPUT_PATH')
CHECKPOINT_PATH = dict_paths.get('CHECKPOINT_PATH')

# COMMAND ----------

dict_tables = get_medallion_tables()
BRONZE_TB_RAW_CLIENTES = dict_tables.get('BRONZE_TB_RAW_CLIENTES')

# COMMAND ----------

print('SCHEMA_PATH\t:', SCHEMA_PATH)
print('INPUT_PATH\t:', INPUT_PATH)
print('CHECKPOINT_PATH\t:', CHECKPOINT_PATH)
print('BRONZE_TB_RAW_CLIENTES\t:', BRONZE_TB_RAW_CLIENTES)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pipeline Parameters

# COMMAND ----------

dbutils.widgets.text('STR_INGESTION_DATE', '2025-05-01')

# COMMAND ----------

STR_INGESTION_DATE = dbutils.widgets.get("STR_INGESTION_DATE")
INGESTION_TIMESTAMP = datetime.strptime(STR_INGESTION_DATE, '%Y-%m-%d') if STR_INGESTION_DATE else datetime.now()

# COMMAND ----------

print('STR_INGESTION_DATE\t:', STR_INGESTION_DATE)
print('INGESTION_TIMESTAMP\t:', INGESTION_TIMESTAMP)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Process

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
    .table(BRONZE_TB_RAW_CLIENTES)
)