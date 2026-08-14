# Databricks notebook source
# DBTITLE 1,Load parameters
# MAGIC %run ./config/parameters

# COMMAND ----------

# DBTITLE 1,Read parameters
CATALOG = params['catalog']
PREFIX  = params['prefix']

# COMMAND ----------

# DBTITLE 1,Build table names
table_bronze     = f'{CATALOG}.bronze.{PREFIX}_sql_pro_input'
table_silver     = f'{CATALOG}.silver.{PREFIX}_sql_pro_transform'
table_quarantine = f'{CATALOG}.silver.{PREFIX}_sql_pro_quarantine'
table_gold       = f'{CATALOG}.gold.{PREFIX}_sql_pro_summary'

tables_to_drop = [table_bronze, table_silver, table_quarantine, table_gold]

# COMMAND ----------

# DBTITLE 1,Drop target tables
for table_name in tables_to_drop:
    spark.sql(f"DROP TABLE IF EXISTS {table_name}")
    print(f"- Table {table_name} dropped")