# Databricks notebook source
my_catalog = 'gx_catalog'
my_prefix = 'atm'

# COMMAND ----------

table_input = f'{my_catalog}.default.{my_prefix}_basic_input'
table_transform = f'{my_catalog}.default.{my_prefix}_basic_transform'
table_summary = f'{my_catalog}.default.{my_prefix}_basic_summary'

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {table_input}')
spark.sql(f'DROP TABLE IF EXISTS {table_transform}')
spark.sql(f'DROP TABLE IF EXISTS {table_summary}')