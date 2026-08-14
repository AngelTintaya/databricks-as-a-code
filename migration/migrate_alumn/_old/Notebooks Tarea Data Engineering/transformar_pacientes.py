# Databricks notebook source
# dbutils.widgets.text("TABLE_INPUT_PACIENTES", "g5_catalog.bronze.pacientes_input")
# dbutils.widgets.text("TABLE_TRANSFORM_PACIENTES", "g5_catalog.silver.pacientes_transform")

# COMMAND ----------

TABLE_INPUT_PACIENTES = dbutils.widgets.get("TABLE_INPUT_PACIENTES")
TABLE_TRANSFORM_PACIENTES = dbutils.widgets.get("TABLE_TRANSFORM_PACIENTES")

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS ${TABLE_TRANSFORM_PACIENTES}

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE ${TABLE_TRANSFORM_PACIENTES} AS
# MAGIC SELECT
# MAGIC     id_paciente,
# MAGIC     edad,
# MAGIC     sexo,
# MAGIC     zona,
# MAGIC     dni,
# MAGIC     direccion,
# MAGIC     latitud,
# MAGIC     longitud,
# MAGIC     id_hospital_cercano,
# MAGIC     distancia_hospital_m,
# MAGIC
# MAGIC     -- Cálculo: clasifica la edad en rangos
# MAGIC     CASE
# MAGIC         WHEN edad < 18 THEN 'menor'
# MAGIC         WHEN edad BETWEEN 18 AND 59 THEN 'adulto'
# MAGIC         ELSE 'adulto mayor'
# MAGIC     END AS grupo_etario,
# MAGIC
# MAGIC     -- Cálculo: rural vs periurbana como dummy
# MAGIC     CASE
# MAGIC         WHEN zona = 'rural' THEN 1
# MAGIC         ELSE 0
# MAGIC     END AS es_rural,
# MAGIC
# MAGIC     -- Cálculo: distancia en kilómetros
# MAGIC     distancia_hospital_m / 1000 AS distancia_hospital_km
# MAGIC
# MAGIC FROM ${TABLE_INPUT_PACIENTES};
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ${TABLE_TRANSFORM_PACIENTES} LIMIT 10

# COMMAND ----------

