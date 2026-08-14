# Databricks notebook source
from pyspark.sql.functions import col

# COMMAND ----------

# dbutils.widgets.text("TABLE_INPUT", "g0_catalog.default.bronze_spark_input")
# dbutils.widgets.text("TABLE_TRANSFORM", "g0_catalog.default.silver_spark_transform")

# COMMAND ----------

table_input = dbutils.widgets.get("TABLE_INPUT")
table_transform = dbutils.widgets.get("TABLE_TRANSFORM")

# COMMAND ----------

df_input = spark.table(table_input)
df_input = df_input.withColumn('total', col('cantidad') * col('precio'))
df_input.write.format("delta").mode("overwrite").saveAsTable(table_transform)

# COMMAND ----------

# spark.sql(f'SELECT * FROM {table_trasnform}').display()