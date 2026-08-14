# Databricks notebook source
CATALOG = 'gx_catalog'

# COMMAND ----------

model_path = "abfss://datalake@stdemdsai.dfs.core.windows.net/models/fraud/lr_model"
dbutils.fs.rm(model_path, recurse=True)

fraud_data = "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/fraud/unlabeled/fraud_data_3.csv"
dbutils.fs.rm(fraud_data, recurse=True)

# COMMAND ----------

checkpoint_streaming_predictions = "abfss://datalake@stdemdsai.dfs.core.windows.net/_checkpoints/streaming_predictions"
dbutils.fs.rm(checkpoint_streaming_predictions, recurse=True)

# COMMAND ----------

table_streaming_predictions = f'{CATALOG}.default.streaming_predictions'
spark.sql(f'DROP TABLE IF EXISTS {table_streaming_predictions}')