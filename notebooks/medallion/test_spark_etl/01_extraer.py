# Databricks notebook source
# DBTITLE 1,Load parameters
# MAGIC %run ./config/parameters

# COMMAND ----------

# DBTITLE 1,Imports
from pyspark.sql.functions import current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

# COMMAND ----------

# DBTITLE 1,Resolve parameters
CATALOG = params['catalog']
PREFIX = params['prefix']
SOURCE_PATH = params['source_path']

table_input = f'{CATALOG}.bronze.{PREFIX}_spark_input'

source_schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("producto", StringType(), True),
    StructField("cantidad", IntegerType(), True),
    StructField("precio", DoubleType(), True)
])

print(f'CATALOG: {CATALOG}')
print(f'PREFIX: {PREFIX}')
print(f'SOURCE_PATH: {SOURCE_PATH}')
print(f'Target table: {table_input}')

# COMMAND ----------

# DBTITLE 1,Read source data
df_input = (
    spark.read
    .option("header", "true")
    .option("mode", "FAILFAST")
    .schema(source_schema)
    .csv(SOURCE_PATH)
)

print('Source schema loaded successfully')

# COMMAND ----------

# DBTITLE 1,Add audit column
df_input = df_input.withColumn("inserted_at", current_timestamp())

# COMMAND ----------

# DBTITLE 1,Write Delta table
(
    df_input.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(table_input)
)

print(f'Data written to {table_input}')

# COMMAND ----------

# DBTITLE 1,Validate load
target_df = spark.table(table_input)
print(f'Rows written: {target_df.count()}')
display(target_df.orderBy("id").limit(5))