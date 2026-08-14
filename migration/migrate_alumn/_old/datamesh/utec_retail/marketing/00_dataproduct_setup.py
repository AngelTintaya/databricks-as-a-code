# Databricks notebook source
# MAGIC %md
# MAGIC # Creación de Schemas

# COMMAND ----------

BRONZE_SCHEMA = 'g0_mkt_clientes.bronze'
SILVER_SCHEMA = 'g0_mkt_clientes.silver'
GOLD_SCHEMA = 'g0_mkt_clientes.gold'
SUPPORT_SCHEMA = 'g0_mkt_clientes.support'

# COMMAND ----------

spark.sql(f'DROP SCHEMA IF EXISTS {BRONZE_SCHEMA} CASCADE')
spark.sql(f'DROP SCHEMA IF EXISTS {SILVER_SCHEMA} CASCADE')
spark.sql(f'DROP SCHEMA IF EXISTS {GOLD_SCHEMA} CASCADE')
spark.sql(f'DROP SCHEMA IF EXISTS {SUPPORT_SCHEMA} CASCADE')

# COMMAND ----------

spark.sql(f'CREATE DATABASE {BRONZE_SCHEMA}')
spark.sql(f'CREATE DATABASE {SILVER_SCHEMA}')
spark.sql(f'CREATE DATABASE {GOLD_SCHEMA}')
spark.sql(f'CREATE DATABASE {SUPPORT_SCHEMA}')