# Databricks notebook source
from pyspark.sql.functions import current_date, lit, current_timestamp
from pyspark.sql.types import StructType, StructField, TimestampType, StringType, IntegerType, DoubleType

# COMMAND ----------

# dbutils.widgets.text("TABLE_INPUT", "g0_catalog.default.bronze_spark_input")

# COMMAND ----------

table_input = dbutils.widgets.get("TABLE_INPUT")

# COMMAND ----------

source_path = "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/input.csv"

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("producto", StringType(), True),
    StructField("cantidad", IntegerType(), True),
    StructField("precio", DoubleType(), True)
])

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {table_input}')

# COMMAND ----------

df_input = (
    spark.read
    .option("header", "true")
    .schema(schema)
    .csv(source_path)
)

# COMMAND ----------

df_input = df_input.withColumn("inserted_at", current_timestamp())

# COMMAND ----------

df_input.write.format("delta").mode("overwrite").saveAsTable(table_input)

# COMMAND ----------

# spark.sql(f'SELECT * FROM {table_input}').display()