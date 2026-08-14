# Databricks notebook source
# DBTITLE 1,Load parameters
# MAGIC %run ./config/parameters

# COMMAND ----------

# DBTITLE 1,Read parameters
CATALOG = params['catalog']
PREFIX = params['prefix']

print(f'CATALOG: {CATALOG}')
print(f'PREFIX: {PREFIX}')

# COMMAND ----------

# DBTITLE 1,Build table names
table_input = f'{CATALOG}.bronze.{PREFIX}_spark_input'
table_transform = f'{CATALOG}.silver.{PREFIX}_spark_transform'
table_summary = f'{CATALOG}.gold.{PREFIX}_spark_summary'

tables_to_drop = [table_input, table_transform, table_summary]

# COMMAND ----------

# DBTITLE 1,Drop target tables
for table_name in tables_to_drop:
    spark.sql(f"DROP TABLE IF EXISTS {table_name}")
    print(f"- Table {table_name} dropped")