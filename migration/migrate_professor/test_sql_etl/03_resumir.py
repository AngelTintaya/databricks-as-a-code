# Databricks notebook source
# dbutils.widgets.text("TABLE_TRANSFORM", "g0_catalog.default.silver_sql_transform")
# dbutils.widgets.text("TABLE_SUMMARY", "g0_catalog.default.gold_sql_summary")

# COMMAND ----------

TABLE_TRANSFORM = dbutils.widgets.get("TABLE_TRANSFORM")
TABLE_SUMMARY = dbutils.widgets.get("TABLE_SUMMARY")

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS ${TABLE_SUMMARY}

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE ${TABLE_SUMMARY} AS
# MAGIC SELECT
# MAGIC   producto,
# MAGIC   SUM(total) AS total_sum
# MAGIC FROM ${TABLE_TRANSFORM}
# MAGIC GROUP BY producto

# COMMAND ----------

# MAGIC %sql
# MAGIC -- SELECT * FROM g0_catalog.default.sql_summary