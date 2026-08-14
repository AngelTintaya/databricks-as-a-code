# Databricks notebook source
dbutils.widgets.text("TABLE_INPUT_PACIENTES", "g5_catalog.bronze.pacientes_input")

# COMMAND ----------

TABLE_INPUT_PACIENTES = dbutils.widgets.get("TABLE_INPUT_PACIENTES")

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS ${TABLE_INPUT_PACIENTES}

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE ${TABLE_INPUT_PACIENTES} AS
# MAGIC SELECT *, current_timestamp() AS inserted_at FROM read_files(
# MAGIC   'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G5/uploaded_pacientes_20250610.csv',
# MAGIC   format => 'csv',
# MAGIC   header => true,
# MAGIC   inferSchema => true,
# MAGIC   ignoreLeadingWhiteSpace => true,
# MAGIC   ignoreTrailingWhiteSpace => true
# MAGIC   -- schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
# MAGIC )

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ${TABLE_INPUT_PACIENTES} LIMIT 10

# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   CASE WHEN COUNT(*) > 0 THEN raise_error('ID is null')
# MAGIC        ELSE 'Datos validados: No hay ID nulos'
# MAGIC   END AS resultados
# MAGIC FROM g0_catalog.default.bronze_sql_input
# MAGIC WHERE id IS NULL

# COMMAND ----------

# MAGIC %sql
# MAGIC -- SELECT * FROM g0_catalog.default.bronze_sql_input