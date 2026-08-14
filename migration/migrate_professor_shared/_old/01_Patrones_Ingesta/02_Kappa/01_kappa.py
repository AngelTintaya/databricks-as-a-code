# Databricks notebook source
CATALOG = 'gx_catalog'

# COMMAND ----------

table_all_tweets_kappa = f'{CATALOG}.default.all_tweets_kappa'
spark.sql(f'DROP TABLE IF EXISTS {table_all_tweets_kappa}')

# COMMAND ----------

checkpoint_all_tweets_kappa = "abfss://datalake@stdemdsai.dfs.core.windows.net/_checkpoints/g0/all_tweets_kappa"
dbutils.fs.rm(checkpoint_all_tweets_kappa, recurse=True)

# COMMAND ----------

from pyspark.sql.functions import current_date, lit
from pyspark.sql.types import StructType, StructField, TimestampType, StringType

source_path = "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/tweets/"

schema = StructType([
    StructField("created_at", TimestampType(), True),
    StructField("current_comment", StringType(), True)
])

# Leer tweets nuevos desde hoy
stream_df = (
    spark.readStream
    .format("csv")
    .option("header", "true")
    .schema(schema)
    .load(source_path)
)

# Añadir columna para identificar origen de los datos
stream_result = stream_df.withColumn("source", lit("stream"))

# Guardar los tweets en tiempo real
query = (
    stream_result.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", checkpoint_all_tweets_kappa)
    .toTable(table_all_tweets_kappa)
)

# COMMAND ----------

spark.sql(f'SELECT * FROM {table_all_tweets_kappa}').display()

# COMMAND ----------

dbutils.fs.cp(
    "abfss://datalake@stdemdsai.dfs.core.windows.net/demo_sources/tweets/new_tweet_5.csv",
    "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/tweets/new_tweet_5.csv"
    )

# COMMAND ----------

spark.sql(f'SELECT * FROM {table_all_tweets_kappa}').display()