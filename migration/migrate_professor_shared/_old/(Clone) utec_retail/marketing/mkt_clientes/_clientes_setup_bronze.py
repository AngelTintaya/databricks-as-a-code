# Databricks notebook source
# MAGIC %run ./__clientes_parameter

# COMMAND ----------

dict_paths = get_paths()
SCHEMA_PATH = dict_paths.get('SCHEMA_PATH')
CHECKPOINT_PATH = dict_paths.get('CHECKPOINT_PATH')

# COMMAND ----------

dict_tables = get_medallion_tables()
BRONZE_TB_RAW_CLIENTES = dict_tables.get('BRONZE_TB_RAW_CLIENTES')

# COMMAND ----------

# Cleaning data
dbutils.fs.rm(SCHEMA_PATH, recurse=True)
dbutils.fs.rm(CHECKPOINT_PATH, recurse=True)
spark.sql(f'DROP TABLE IF EXISTS {BRONZE_TB_RAW_CLIENTES}')