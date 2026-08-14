# Databricks notebook source
dbutils.widgets.text("TABLE_INPUT_HOSPITALES", "g5_catalog.bronze.hospitales_input")
dbutils.widgets.text("TABLE_TRANSFORM_HOSPITALES", "g5_catalog.silver.hospitales_transform")

# COMMAND ----------

TABLE_INPUT_HOSPITALES = dbutils.widgets.get("TABLE_INPUT_HOSPITALES")
TABLE_TRANSFORM_HOSPITALES = dbutils.widgets.get("TABLE_TRANSFORM_HOSPITALES")

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS ${TABLE_TRANSFORM_HOSPITALES}

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE ${TABLE_TRANSFORM_HOSPITALES} AS
# MAGIC SELECT
# MAGIC     id_hospital,
# MAGIC     nombre,
# MAGIC     departamento,
# MAGIC     latitud,
# MAGIC     longitud,
# MAGIC     especialidades,
# MAGIC
# MAGIC     -- Número total de especialidades
# MAGIC     size(especialidades) AS num_especialidades,
# MAGIC
# MAGIC     -- Clasificador para hospitales con alta diversidad de atención
# MAGIC     CASE
# MAGIC         WHEN size(especialidades) >= 5 THEN 'complejo'
# MAGIC         WHEN size(especialidades) >= 3 THEN 'intermedio'
# MAGIC         ELSE 'básico'
# MAGIC     END AS tipo_hospital,
# MAGIC
# MAGIC     -- Clasificación geográfica simple por latitud
# MAGIC     CASE
# MAGIC         WHEN latitud < -12 THEN 'zona sur'
# MAGIC         WHEN latitud BETWEEN -12 AND -6 THEN 'zona centro'
# MAGIC         ELSE 'zona norte'
# MAGIC     END AS zona_geografica
# MAGIC
# MAGIC FROM ${TABLE_INPUT_HOSPITALES};
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ${TABLE_TRANSFORM_HOSPITALES} LIMIT 10

# COMMAND ----------

