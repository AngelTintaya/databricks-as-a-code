# Databricks notebook source
from pyspark.sql.functions import col, sum

# COMMAND ----------

# dbutils.widgets.text("TABLE_TRANSFORM", "g0_catalog.default.silver_spark_transform")
# dbutils.widgets.text("TABLE_SUMMARY", "g0_catalog.default.gold_spark_summary")

# COMMAND ----------

table_transform = dbutils.widgets.get("TABLE_TRANSFORM")
table_summary = dbutils.widgets.get("TABLE_SUMMARY")

# COMMAND ----------

df_transform = spark.table(table_transform)
df_summary = df_transform.groupBy('producto').agg(sum('total').alias('total_sum'))
df_summary.write.format("delta").mode("overwrite").saveAsTable(table_summary)

# COMMAND ----------

# spark.sql(f'SELECT * FROM {table_summary}').display()