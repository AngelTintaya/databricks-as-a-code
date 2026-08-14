# Databricks notebook source
# dbutils.widgets.text("TABLE_TRANSFORM_BD_MEDICA", "g5_catalog.silver.bd_medica_transform")
# dbutils.widgets.text("TABLE_SUMMARY_BD_MEDICA", "g5_catalog.gold.bd_medica_summary")

# COMMAND ----------

TABLE_TRANSFORM_BD_MEDICA = dbutils.widgets.get("TABLE_TRANSFORM_BD_MEDICA")
TABLE_SUMMARY_BD_MEDICA = dbutils.widgets.get("TABLE_SUMMARY_BD_MEDICA")

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS ${TABLE_SUMMARY_BD_MEDICA}

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE ${TABLE_SUMMARY_BD_MEDICA} AS
# MAGIC SELECT
# MAGIC     enfermedad,
# MAGIC     COUNT(*) AS total_casos,
# MAGIC     
# MAGIC     -- Síntoma más frecuente por enfermedad
# MAGIC     FIRST(sintoma) AS sintoma_frecuente,
# MAGIC     
# MAGIC     ROUND(AVG(temperatura), 1) AS temperatura_prom,
# MAGIC     ROUND(AVG(presion), 1) AS presion_prom,
# MAGIC     
# MAGIC     -- Intentar convertir glucosa a numérica, si no ya debe ser DOUBLE
# MAGIC     ROUND(AVG(TRY_CAST(glucosa AS DOUBLE)), 1) AS glucosa_prom
# MAGIC
# MAGIC FROM ${TABLE_TRANSFORM_BD_MEDICA}
# MAGIC GROUP BY enfermedad;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ${TABLE_SUMMARY_BD_MEDICA}