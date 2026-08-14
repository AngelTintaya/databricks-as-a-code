# Databricks notebook source
# MAGIC %run ../../utils/general

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS g0_mkt_clientes.bronze.raw_clientes;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE g0_mkt_clientes.bronze.raw_clientes AS
# MAGIC SELECT *, current_timestamp() AS inserted_at FROM read_files(
# MAGIC   -- 'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/clientes.csv',
# MAGIC   'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/clientes/',
# MAGIC   format => 'csv',
# MAGIC   header => true,
# MAGIC   inferSchema => true
# MAGIC   --schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
# MAGIC )

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE HISTORY g0_mkt_clientes.bronze.raw_clientes