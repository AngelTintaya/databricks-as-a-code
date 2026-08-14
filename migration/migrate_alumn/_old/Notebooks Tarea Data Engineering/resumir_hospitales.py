# Databricks notebook source
 dbutils.widgets.text("TABLE_TRANSFORM_HOSPITALES", "g5_catalog.silver.hospitales_transform")
 dbutils.widgets.text("TABLE_SUMMARY_HOSPITALES", "g5_catalog.gold.hospitales_summary")

# COMMAND ----------

TABLE_TRANSFORM_HOSPITALES = dbutils.widgets.get("TABLE_TRANSFORM_HOSPITALES")
TABLE_SUMMARY_HOSPITALES = dbutils.widgets.get("TABLE_SUMMARY_HOSPITALES")

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS ${TABLE_SUMMARY_HOSPITALES}

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE ${TABLE_SUMMARY_HOSPITALES} AS
# MAGIC SELECT
# MAGIC     zona_geografica,
# MAGIC     tipo_hospital,
# MAGIC     COUNT(*) AS total_hospitales,
# MAGIC     ROUND(AVG(num_especialidades), 2) AS promedio_especialidades,
# MAGIC     SUM(num_especialidades) AS total_especialidades
# MAGIC
# MAGIC FROM ${TABLE_TRANSFORM_HOSPITALES}
# MAGIC GROUP BY zona_geografica, tipo_hospital;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ${TABLE_SUMMARY_HOSPITALES}