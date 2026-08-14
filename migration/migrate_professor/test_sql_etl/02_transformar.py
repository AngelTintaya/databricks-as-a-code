# Databricks notebook source
# dbutils.widgets.text("TABLE_INPUT", "g0_catalog.default.bronze_sql_input")
# dbutils.widgets.text("TABLE_TRANSFORM", "g0_catalog.default.silver_sql_transform")

# COMMAND ----------

TABLE_INPUT = dbutils.widgets.get("TABLE_INPUT")
TABLE_TRANSFORM = dbutils.widgets.get("TABLE_TRANSFORM")

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS ${TABLE_TRANSFORM}

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE ${TABLE_TRANSFORM} AS 
# MAGIC SELECT
# MAGIC     inp.id,
# MAGIC     inp.producto,
# MAGIC     inp.cantidad,
# MAGIC     inp.precio,
# MAGIC     inp.inserted_at,
# MAGIC     inp.cantidad * inp.precio AS total
# MAGIC FROM ${TABLE_INPUT} inp

# COMMAND ----------

# MAGIC %sql
# MAGIC -- SELECT * FROM g0_catalog.default.sql_transform