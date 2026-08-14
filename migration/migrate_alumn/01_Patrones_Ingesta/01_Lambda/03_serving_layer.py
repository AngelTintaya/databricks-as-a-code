# Databricks notebook source
# MAGIC %md
# MAGIC ### Serving Layer: Combinamos ambos resultados

# COMMAND ----------

CATALOG = 'gx_catalog'

# COMMAND ----------

table_historical_tweets = f'{CATALOG}.default.historical_tweets'
table_realtime_tweets = f'{CATALOG}.default.realtime_tweets'
view_all_tweets = f'{CATALOG}.default.all_tweets'

spark.sql(f'DROP VIEW IF EXISTS {view_all_tweets}')

# COMMAND ----------

spark.sql(f"""
          CREATE OR REPLACE VIEW {view_all_tweets} AS
          SELECT * FROM {table_historical_tweets}
          UNION ALL
          SELECT * FROM {table_realtime_tweets}
          """)

# COMMAND ----------

df_all_tweets = spark.sql(f'SELECT * FROM {view_all_tweets}')
df_all_tweets.display()

# COMMAND ----------

dbutils.fs.cp(
    "abfss://datalake@stdemdsai.dfs.core.windows.net/demo_sources/tweets/new_tweet_3.csv",
    "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/tweets/new_tweet_3.csv"
    )

# COMMAND ----------

df_all_tweets = spark.sql(f'SELECT * FROM {view_all_tweets}')
df_all_tweets.display()