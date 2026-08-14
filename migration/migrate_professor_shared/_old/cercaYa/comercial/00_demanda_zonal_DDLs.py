# Databricks notebook source
my_catalog = 'g204_cmc_demanda_zonal'

# COMMAND ----------

spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.bronze.raw_ventas_darkstore""")

# COMMAND ----------

spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.bronze.raw_envios""")