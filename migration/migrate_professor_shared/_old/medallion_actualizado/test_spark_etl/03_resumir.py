# Databricks notebook source
# DBTITLE 1,Load parameters
# MAGIC %run ./config/parameters

# COMMAND ----------

# DBTITLE 1,Imports
from pyspark.sql.functions import sum

# COMMAND ----------

# DBTITLE 1,Resolve parameters
CATALOG = params['catalog']
PREFIX = params['prefix']

table_transform = f'{CATALOG}.silver.{PREFIX}_spark_transform'
table_summary = f'{CATALOG}.gold.{PREFIX}_spark_summary'

print(f'CATALOG: {CATALOG}')
print(f'PREFIX: {PREFIX}')
print(f'Source table: {table_transform}')
print(f'Target table: {table_summary}')

# COMMAND ----------

# DBTITLE 1,Build summary
df_transform = spark.table(table_transform)
df_summary = df_transform.groupBy('producto').agg(sum('total').alias('total_sum'))

# COMMAND ----------

# DBTITLE 1,Write summary table
(
    df_summary.write
    .format('delta')
    .mode('overwrite')
    .saveAsTable(table_summary)
)

print(f'Data written to {table_summary}')

# COMMAND ----------

# DBTITLE 1,Validate output
df_target = spark.table(table_summary)
df_preview = df_target.limit(5)

print(f'Validation preview for {table_summary}')
display(df_preview)