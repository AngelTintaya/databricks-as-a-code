# Databricks notebook source
my_catalog = 'gx_catalog'
my_prefix = 'atm'

# COMMAND ----------

table_input = f'{my_catalog}.bronze.{my_prefix}_sql_input'
table_transform = f'{my_catalog}.silver.{my_prefix}_sql_transform'
table_summary = f'{my_catalog}.gold.{my_prefix}_sql_summary'

# COMMAND ----------

spark.sql(f"""DROP TABLE IF EXISTS {table_input}""")
spark.sql(f"""DROP TABLE IF EXISTS {table_transform}""")
spark.sql(f"""DROP TABLE IF EXISTS {table_summary}""")