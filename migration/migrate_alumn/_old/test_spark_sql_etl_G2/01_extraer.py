# Databricks notebook source
dbutils.widgets.text("TABLE_INPUT", "g6_catalog.bronze.spark_sql_input")

# COMMAND ----------

TABLE_INPUT = dbutils.widgets.get("TABLE_INPUT")

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {TABLE_INPUT}')

# COMMAND ----------

spark.sql(f"""
          CREATE OR REPLACE TABLE {TABLE_INPUT} AS
          SELECT *, current_timestamp() AS inserted_at
          FROM read_files(
              'abfss://datalake@stdemdsai.dfs.core.windows.net//raw/airflow/g06/despachos_20250531.csv',
              format => 'csv',
              header => true,
              inferSchema => true
              )
          """)