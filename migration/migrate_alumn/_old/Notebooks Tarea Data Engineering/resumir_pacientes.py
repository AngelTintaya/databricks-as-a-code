# Databricks notebook source
 # dbutils.widgets.text("TABLE_TRANSFORM_PACIENTES", "g5_catalog.silver.pacientes_transform")
 # dbutils.widgets.text("TABLE_SUMMARY_PACIENTES", "g5_catalog.gold.pacientes_summary")

# COMMAND ----------

TABLE_TRANSFORM_PACIENTES = dbutils.widgets.get("TABLE_TRANSFORM_PACIENTES")
TABLE_SUMMARY_PACIENTES = dbutils.widgets.get("TABLE_SUMMARY_PACIENTES")

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS ${TABLE_SUMMARY_PACIENTES}

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE ${TABLE_SUMMARY_PACIENTES} AS
# MAGIC SELECT
# MAGIC     zona,
# MAGIC     grupo_etario,
# MAGIC     COUNT(*) AS num_pacientes,
# MAGIC     ROUND(AVG(edad), 1) AS edad_promedio,
# MAGIC     ROUND(AVG(distancia_hospital_km), 2) AS distancia_promedio_km
# MAGIC FROM ${TABLE_TRANSFORM_PACIENTES}
# MAGIC GROUP BY zona, grupo_etario;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ${TABLE_SUMMARY_PACIENTES}