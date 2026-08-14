# Databricks notebook source
# DBTITLE 1,Load parameters
# MAGIC %run ./config/parameters

# COMMAND ----------

# DBTITLE 1,Configure widget
dbutils.widgets.text("descuento", "0.1")

# COMMAND ----------

# DBTITLE 1,Imports
from pyspark.sql.functions import col, lit

# COMMAND ----------

# DBTITLE 1,Resolve parameters
CATALOG = params['catalog']
PREFIX = params['prefix']
DISCOUNT = float(dbutils.widgets.get("descuento"))
MULTIPLIER = 1 - DISCOUNT

table_input = f'{CATALOG}.bronze.{PREFIX}_spark_input'
table_transform = f'{CATALOG}.silver.{PREFIX}_spark_transform'

print(f'CATALOG: {CATALOG}')
print(f'PREFIX: {PREFIX}')
print(f'Discount: {DISCOUNT}')
print(f'Multiplier: {MULTIPLIER}')
print(f'Source table: {table_input}')
print(f'Target table: {table_transform}')

# COMMAND ----------

# DBTITLE 1,Transform totals
df_input = spark.table(table_input)
df_transform = (
    df_input
    .withColumn('descuento', lit(DISCOUNT))
    .withColumn('total', col('cantidad') * col('precio') * lit(MULTIPLIER))
)

# COMMAND ----------

# DBTITLE 1,Write to table
(
    df_transform.write
    .format('delta')
    .mode('overwrite')
    .saveAsTable(table_transform)
)

print(f'Data written to {table_transform}')

# COMMAND ----------

# DBTITLE 1,Validate output
df_target = spark.table(table_transform)
df_preview = df_target.limit(5)

print(f'Validation preview for {table_transform}')
display(df_preview)