# Databricks notebook source
# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE g0_catalog.default.atm_basic_input AS
# MAGIC SELECT *, current_timestamp() AS inserted_at FROM read_files(
# MAGIC   'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/input.csv',
# MAGIC   format => 'csv',
# MAGIC   header => true,
# MAGIC   inferSchema => true,
# MAGIC   ignoreLeadingWhiteSpace => true,
# MAGIC   ignoreTrailingWhiteSpace => true
# MAGIC   -- schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
# MAGIC )

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE g0_catalog.default.atm_basic_transform AS 
# MAGIC SELECT
# MAGIC     inp.id,
# MAGIC     inp.producto,
# MAGIC     inp.cantidad,
# MAGIC     inp.precio,
# MAGIC     inp.inserted_at,
# MAGIC     inp.cantidad * inp.precio AS total
# MAGIC FROM g0_catalog.default.atm_basic_input inp
# MAGIC WHERE inp.id IS NOT NULL

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE g0_catalog.default.atm_basic_summary AS
# MAGIC SELECT
# MAGIC   producto,
# MAGIC   SUM(total) AS total_sum
# MAGIC FROM g0_catalog.default.atm_basic_transform
# MAGIC GROUP BY producto