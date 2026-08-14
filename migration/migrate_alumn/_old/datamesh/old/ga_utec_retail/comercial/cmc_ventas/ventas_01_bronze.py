# Databricks notebook source
# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS ga_cmc_ventas.bronze.raw_ventas_ecommerce

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS ga_cmc_ventas.bronze.raw_ventas_tienda

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE ga_cmc_ventas.bronze.raw_ventas_ecommerce
# MAGIC AS
# MAGIC SELECT *, current_timestamp() AS inserted_at
# MAGIC FROM read_files(
# MAGIC     'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/ventas/ecommerce/',
# MAGIC     format => 'csv',
# MAGIC     header => true,
# MAGIC     inferSchema => true
# MAGIC     --schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
# MAGIC     )

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE ga_cmc_ventas.bronze.raw_ventas_tienda
# MAGIC AS
# MAGIC SELECT *, current_timestamp() AS inserted_at
# MAGIC FROM read_files(
# MAGIC     'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/ventas/tienda/',
# MAGIC     format => 'csv',
# MAGIC     header => true,
# MAGIC     inferSchema => true
# MAGIC     --schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
# MAGIC     )