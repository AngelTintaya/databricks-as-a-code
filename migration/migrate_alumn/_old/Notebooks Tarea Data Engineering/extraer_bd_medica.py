# Databricks notebook source
dbutils.widgets.text("TABLE_INPUT_BD_MEDICA", "g5_catalog.bronze.bd_medica_input")

# COMMAND ----------

TABLE_INPUT_BD_MEDICA = dbutils.widgets.get("TABLE_INPUT_BD_MEDICA")

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS ${TABLE_INPUT_BD_MEDICA}

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE ${TABLE_INPUT_BD_MEDICA} AS
# MAGIC SELECT *, current_timestamp() AS inserted_at FROM read_files(
# MAGIC   'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G5/uploaded_bd_medica_20250610.csv',
# MAGIC   format => 'csv',
# MAGIC   header => true,
# MAGIC   inferSchema => true,
# MAGIC   ignoreLeadingWhiteSpace => true,
# MAGIC   ignoreTrailingWhiteSpace => true
# MAGIC   -- schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
# MAGIC )

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ${TABLE_INPUT_BD_MEDICA} LIMIT 10

# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------

