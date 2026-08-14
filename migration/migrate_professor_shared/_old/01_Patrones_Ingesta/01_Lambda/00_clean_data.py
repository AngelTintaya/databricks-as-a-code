# Databricks notebook source
CATALOG = 'gx_catalog'

# COMMAND ----------

table_historical_tweets = f'{CATALOG}.default.historical_tweets'
table_realtime_tweets = f'{CATALOG}.default.realtime_tweets'
view_all_tweets = f'{CATALOG}.default.all_tweets'

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {table_historical_tweets}')
spark.sql(f'DROP TABLE IF EXISTS {table_realtime_tweets}')
spark.sql(f'DROP VIEW IF EXISTS {view_all_tweets}')

# COMMAND ----------

checkpoint_realtime_tweets = "abfss://datalake@stdemdsai.dfs.core.windows.net/_checkpoints/g0/realtime_tweets"
dbutils.fs.rm(checkpoint_realtime_tweets, recurse=True)

# COMMAND ----------

dbutils.fs.rm("abfss://datalake@stdemdsai.dfs.core.windows.net/raw/tweets/new_tweet_1.csv", recurse=True)
dbutils.fs.rm("abfss://datalake@stdemdsai.dfs.core.windows.net/raw/tweets/new_tweet_2.csv", recurse=True)
dbutils.fs.rm("abfss://datalake@stdemdsai.dfs.core.windows.net/raw/tweets/new_tweet_3.csv", recurse=True)
dbutils.fs.rm("abfss://datalake@stdemdsai.dfs.core.windows.net/raw/tweets/new_tweet_4.csv", recurse=True)
dbutils.fs.rm("abfss://datalake@stdemdsai.dfs.core.windows.net/raw/tweets/new_tweet_5.csv", recurse=True)