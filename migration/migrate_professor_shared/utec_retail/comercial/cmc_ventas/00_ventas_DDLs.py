# Databricks notebook source
my_catalog = 'gx00_cmc_ventas'

# COMMAND ----------

spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.bronze.raw_ventas_ecommerce""")

# COMMAND ----------

spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.bronze.raw_ventas_tienda""")