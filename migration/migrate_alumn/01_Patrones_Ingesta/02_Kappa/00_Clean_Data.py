# Databricks notebook source
CATALOG = 'gx_catalog'

# COMMAND ----------

table_all_tweets_kappa = f'{CATALOG}.default.all_tweets_kappa'

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {table_all_tweets_kappa}')

# COMMAND ----------

dbutils.fs.rm("abfss://datalake@stdemdsai.dfs.core.windows.net/_checkpoints/g0/all_tweets_kappa", recurse=True)

# COMMAND ----------

dbutils.fs.rm("abfss://datalake@stdemdsai.dfs.core.windows.net/raw/tweets/new_tweet_5.csv", recurse=True)