# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook **will run** in Pipeline
# MAGIC - Need to create temporary views and insert into fixed raw table
# MAGIC - COMMENT widget creation: dbutils.widgets.text() -> It will be created in the pipeline

# COMMAND ----------

from datetime import datetime, date

# COMMAND ----------

my_catalog = 'g204_ops_entregas'

# COMMAND ----------


dbutils.widgets.text('BRONZE_TB_RAW_ENVIOS', f'{my_catalog}.bronze.raw_envios')
dbutils.widgets.text('STR_INGESTION_DATE', '2026-07-17')

# COMMAND ----------

BRONZE_TB_RAW_ENVIOS = 'g204_ops_entregas.bronze.raw_envios'
STR_INGESTION_DATE = dbutils.widgets.get("STR_INGESTION_DATE")

from datetime import datetime, date
INGESTION_DATE = datetime.strptime(STR_INGESTION_DATE, '%Y-%m-%d').date() if STR_INGESTION_DATE else date.today()

# COMMAND ----------

print('BRONZE_TB_RAW_ENVIOS\t:', BRONZE_TB_RAW_ENVIOS)
print('STR_INGESTION_DATE\t\t:', STR_INGESTION_DATE)
print('INGESTION_DATE\t\t\t:', INGESTION_DATE)

# COMMAND ----------

spark.sql(f"""
          CREATE OR REPLACE TEMPORARY VIEW nuevo_inventario_envios_temp
          AS
          SELECT *, current_timestamp() AS inserted_at FROM read_files(
              'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow2/G04/operaciones/envios_{INGESTION_DATE}.csv',
              format => 'csv',
              header => true,
              inferSchema => true
              )
          """)

# COMMAND ----------

spark.sql(f"""
          CREATE TABLE {BRONZE_TB_RAW_ENVIOS}
          AS 
          SELECT * FROM nuevo_inventario_envios_temp
          """).display()