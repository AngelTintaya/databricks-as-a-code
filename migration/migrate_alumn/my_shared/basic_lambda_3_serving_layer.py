# Databricks notebook source
# MAGIC %md
# MAGIC ### Serving Layer: Combinamos ambos resultados

# COMMAND ----------

table_historical_tweets = 'g0_catalog.default.historical_tweets'
table_realtime_tweets = 'g0_catalog.default.realtime_tweets'
table_all_tweets = 'g0_catalog.default.all_tweets'

spark.sql(f'DROP VIEW IF EXISTS {table_all_tweets}')

# COMMAND ----------

spark.sql(f"""
          CREATE OR REPLACE VIEW {table_all_tweets} AS
          SELECT * FROM {table_historical_tweets}
          UNION ALL
          SELECT * FROM {table_realtime_tweets}
          """)

# COMMAND ----------

df_all_tweets = spark.sql(f'SELECT * FROM {table_all_tweets}')
df_all_tweets.display()