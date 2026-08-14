# Databricks notebook source
# MAGIC %md
# MAGIC ### Speed Layer: Procesa Datos Recientes

# COMMAND ----------

CATALOG = 'gx_catalog'

# COMMAND ----------

table_realtime_tweets = f'{CATALOG}.default.realtime_tweets'
spark.sql(f'DROP TABLE IF EXISTS {table_realtime_tweets}')

# COMMAND ----------

checkpoint_realtime_tweets = "abfss://datalake@stdemdsai.dfs.core.windows.net/_checkpoints/g0/realtime_tweets"
dbutils.fs.rm(checkpoint_realtime_tweets, recurse=True)

# COMMAND ----------

dbutils.fs.rm("abfss://datalake@stdemdsai.dfs.core.windows.net/raw/tweets/new_tweet_1.csv", recurse=True)

# COMMAND ----------

dbutils.fs.cp(
    "abfss://datalake@stdemdsai.dfs.core.windows.net/demo_sources/tweets/new_tweet_1.csv",
    "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/tweets/new_tweet_1.csv"
    )

# COMMAND ----------

from pyspark.sql.functions import current_date, lit
from pyspark.sql.types import StructType, StructField, TimestampType, StringType

source_path = "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/tweets/"
fixed_date = "2025-05-05" 

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
    # .filter("created_at >= current_date()")
    .filter(f"created_at >= DATE('{fixed_date}')")
)

# Añadir columna para identificar origen de los datos
stream_result = stream_df.withColumn("source", lit("stream"))

# Guardar los tweets en tiempo real
query = (
    stream_result.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", checkpoint_realtime_tweets)
    .toTable(table_realtime_tweets)
)


# COMMAND ----------

df_realtime = spark.sql(f'SELECT * FROM {table_realtime_tweets}')
df_realtime.display()

# COMMAND ----------

dbutils.fs.cp(
    "abfss://datalake@stdemdsai.dfs.core.windows.net/demo_sources/tweets/new_tweet_2.csv",
    "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/tweets/new_tweet_2.csv"
    )

# COMMAND ----------

df_realtime = spark.sql(f'SELECT * FROM {table_realtime_tweets}')
df_realtime.display()