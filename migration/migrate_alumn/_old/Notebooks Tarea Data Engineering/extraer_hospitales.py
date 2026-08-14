# Databricks notebook source
dbutils.widgets.text("TABLE_INPUT_HOSPITALES", "g5_catalog.bronze.hospitales_input")

# COMMAND ----------

TABLE_INPUT_HOSPITALES = dbutils.widgets.get("TABLE_INPUT_HOSPITALES")

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS ${TABLE_INPUT_HOSPITALES}

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE ${TABLE_INPUT_HOSPITALES} AS
# MAGIC SELECT *, current_timestamp() AS inserted_at FROM read_files(
# MAGIC   'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G5/uploaded_hospitales_20250610.json',
# MAGIC   format => 'json',
# MAGIC   header => true,
# MAGIC   inferSchema => false,
# MAGIC   ignoreLeadingWhiteSpace => true,
# MAGIC   ignoreTrailingWhiteSpace => true,
# MAGIC   schema => '
# MAGIC     id_hospital INT,
# MAGIC     nombre STRING,
# MAGIC     departamento STRING,
# MAGIC     latitud DOUBLE,
# MAGIC     longitud DOUBLE,
# MAGIC     especialidades ARRAY<STRING>
# MAGIC   '
# MAGIC )

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ${TABLE_INPUT_HOSPITALES} LIMIT 10

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