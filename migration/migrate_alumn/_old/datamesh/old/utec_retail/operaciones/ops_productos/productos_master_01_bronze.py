# Databricks notebook source
# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS g0_ops_productos.bronze.raw_inventario;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE g0_ops_productos.bronze.raw_inventario AS
# MAGIC SELECT *, current_timestamp() AS inserted_at FROM read_files(
# MAGIC   'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/productos/inventario/',
# MAGIC   format => 'csv',
# MAGIC   header => true,
# MAGIC   inferSchema => true
# MAGIC   --schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
# MAGIC )