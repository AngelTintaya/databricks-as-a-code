# Databricks notebook source
my_catalog = 'gx_catalog'
my_prefix = 'atm'

# COMMAND ----------

table_silver = f'{my_catalog}.silver.{my_prefix}_sql_transform'
table_gold = f'{my_catalog}.gold.{my_prefix}_sql_summary'

# COMMAND ----------

spark.sql(f"""DROP TABLE IF EXISTS {table_gold}""")

# COMMAND ----------

spark.sql(
    f"""
    CREATE TABLE {table_gold} AS
    SELECT
        producto,
        SUM(total) AS total_sum
    FROM {table_silver}
    GROUP BY producto
    """
)

# COMMAND ----------

# spark.sql(f"""SELECT * FROM {table_gold}""").display()