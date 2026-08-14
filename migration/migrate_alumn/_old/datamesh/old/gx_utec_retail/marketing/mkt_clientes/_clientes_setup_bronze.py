# Databricks notebook source
# MAGIC %run ./_clientes_parameter

# COMMAND ----------

# Cleaning data
dbutils.fs.rm(SCHEMA_PATH, recurse=True)
dbutils.fs.rm(CHECKPOINT_PATH, recurse=True)
spark.sql('DROP TABLE IF EXISTS g0_mkt_clientes.bronze.raw_clientes')