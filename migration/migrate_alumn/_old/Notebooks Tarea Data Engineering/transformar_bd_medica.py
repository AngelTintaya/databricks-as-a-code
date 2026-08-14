# Databricks notebook source
dbutils.widgets.text("TABLE_INPUT_BD_MEDICA", "g5_catalog.bronze.bd_medica_input")
dbutils.widgets.text("TABLE_TRANSFORM_BD_MEDICA", "g5_catalog.silver.bd_medica_transform")

# COMMAND ----------

TABLE_INPUT_PACIENTES = dbutils.widgets.get("TABLE_INPUT_BD_MEDICA")
TABLE_TRANSFORM_PACIENTES = dbutils.widgets.get("TABLE_TRANSFORM_BD_MEDICA")

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS ${TABLE_TRANSFORM_BD_MEDICA}

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE ${TABLE_TRANSFORM_BD_MEDICA} AS
# MAGIC SELECT
# MAGIC     id_atencion,
# MAGIC     id_paciente,
# MAGIC     fecha,
# MAGIC     temperatura,
# MAGIC     presion,
# MAGIC     glucosa,
# MAGIC     sintoma,
# MAGIC     enfermedad,
# MAGIC
# MAGIC     -- Clasificación por temperatura
# MAGIC     CASE
# MAGIC         WHEN temperatura >= 37.5 THEN 'fiebre alta'
# MAGIC         WHEN temperatura BETWEEN 37.0 AND 37.4 THEN 'febrícula'
# MAGIC         ELSE 'normal'
# MAGIC     END AS nivel_temperatura,
# MAGIC
# MAGIC     -- Clasificación por presión arterial
# MAGIC     CASE
# MAGIC         WHEN presion < 90 THEN 'hipotensión'
# MAGIC         WHEN presion BETWEEN 90 AND 120 THEN 'normal'
# MAGIC         WHEN presion BETWEEN 121 AND 139 THEN 'prehipertensión'
# MAGIC         ELSE 'hipertensión'
# MAGIC     END AS nivel_presion,
# MAGIC
# MAGIC     -- Clasificación por glucosa
# MAGIC     CASE
# MAGIC         WHEN TRY_CAST(glucosa AS DOUBLE) < 70 THEN 'hipoglucemia'
# MAGIC         WHEN TRY_CAST(glucosa AS DOUBLE) BETWEEN 70 AND 99 THEN 'normal'
# MAGIC         WHEN TRY_CAST(glucosa AS DOUBLE) BETWEEN 100 AND 125 THEN 'prediabetes'
# MAGIC         ELSE 'diabetes'
# MAGIC     END AS nivel_glucosa
# MAGIC
# MAGIC FROM ${TABLE_INPUT_BD_MEDICA};
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ${TABLE_TRANSFORM_BD_MEDICA} LIMIT 10

# COMMAND ----------

