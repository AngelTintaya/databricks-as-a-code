# Databricks notebook source
# dbutils.widgets.text("TABLE_INPUT_CONSULTAS_VIRTUALES", "g5_catalog.bronze.consultas_virtuales_input")
# dbutils.widgets.text("TABLE_TRANSFORM_CONSULTAS_VIRTUALES", "g5_catalog.silver.consultas_virtuales_transform")

# COMMAND ----------

TABLE_INPUT_CONSULTAS_VIRTUALES = dbutils.widgets.get("TABLE_INPUT_CONSULTAS_VIRTUALES")
TABLE_TRANSFORM_CONSULTAS_VIRTUALES = dbutils.widgets.get("TABLE_TRANSFORM_CONSULTAS_VIRTUALES")

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS ${TABLE_TRANSFORM_CONSULTAS_VIRTUALES}

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE ${TABLE_TRANSFORM_CONSULTAS_VIRTUALES} AS
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
# MAGIC     -- Clasificación por fiebre
# MAGIC     CASE
# MAGIC         WHEN temperatura >= 38 THEN 'fiebre alta'
# MAGIC         WHEN temperatura BETWEEN 37 AND 37.9 THEN 'febrícula'
# MAGIC         ELSE 'normal'
# MAGIC     END AS estado_fiebre,
# MAGIC
# MAGIC     -- Clasificación por presión arterial
# MAGIC     CASE
# MAGIC         WHEN presion < 90 THEN 'hipotensión'
# MAGIC         WHEN presion BETWEEN 90 AND 120 THEN 'normal'
# MAGIC         WHEN presion BETWEEN 121 AND 139 THEN 'prehipertensión'
# MAGIC         ELSE 'hipertensión'
# MAGIC     END AS estado_presion,
# MAGIC
# MAGIC     -- Clasificación por glucosa (con TRY_CAST por seguridad)
# MAGIC     CASE
# MAGIC         WHEN TRY_CAST(glucosa AS DOUBLE) < 70 THEN 'hipoglucemia'
# MAGIC         WHEN TRY_CAST(glucosa AS DOUBLE) BETWEEN 70 AND 99 THEN 'normal'
# MAGIC         WHEN TRY_CAST(glucosa AS DOUBLE) BETWEEN 100 AND 125 THEN 'prediabetes'
# MAGIC         ELSE 'diabetes'
# MAGIC     END AS estado_glucosa,
# MAGIC
# MAGIC     -- Clasificador binario para enfermedades respiratorias
# MAGIC     CASE
# MAGIC         WHEN enfermedad IN ('COVID-19', 'Gripe') THEN 1
# MAGIC         ELSE 0
# MAGIC     END AS enfermedad_respiratoria
# MAGIC
# MAGIC FROM ${TABLE_INPUT_CONSULTAS_VIRTUALES};
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ${TABLE_TRANSFORM_CONSULTAS_VIRTUALES} LIMIT 10

# COMMAND ----------

