# Databricks notebook source
my_catalog = 'gx_catalog'
my_prefix = 'atm'

# COMMAND ----------

table_bronze = f'{my_catalog}.bronze.{my_prefix}_sql_input'
table_silver = f'{my_catalog}.silver.{my_prefix}_sql_transform'

# COMMAND ----------

spark.sql(f"""DROP TABLE IF EXISTS {table_silver}""")

# COMMAND ----------

spark.sql(
    f"""
    CREATE TABLE {table_silver} AS 
    SELECT
        inp.id,
        inp.producto,
        inp.cantidad,
        inp.precio,
        inp.inserted_at,
        inp.cantidad * inp.precio AS total
    FROM {table_bronze} inp
    """
)

# COMMAND ----------

# spark.sql(f"""SELECT * FROM {table_silver}""").display()