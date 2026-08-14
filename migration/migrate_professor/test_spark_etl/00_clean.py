# Databricks notebook source
table_input = 'g0_catalog.default.bronze_spark_input'
table_transform = 'g0_catalog.default.silver_spark_transform'
table_summary = 'g0_catalog.default.gold_spark_summary'

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {table_input}')
spark.sql(f'DROP TABLE IF EXISTS {table_transform}')
spark.sql(f'DROP TABLE IF EXISTS {table_summary}')