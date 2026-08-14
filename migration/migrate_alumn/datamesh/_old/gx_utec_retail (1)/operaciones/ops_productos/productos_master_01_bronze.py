# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook **will run** in Pipeline
# MAGIC - Need to create temporary views and insert into fixed raw table
# MAGIC - COMMENT widget creation: dbutils.widgets.text() -> It will be created in the pipeline

# COMMAND ----------

from datetime import datetime, date

# COMMAND ----------

# dbutils.widgets.text('BRONZE_TB_RAW_INVENTARIO', 'gx_ops_productos.bronze.raw_inventario')
# dbutils.widgets.text('STR_INGESTION_DATE', '2024-01-01')

# COMMAND ----------

BRONZE_TB_RAW_INVENTARIO = dbutils.widgets.get("BRONZE_TB_RAW_INVENTARIO")
STR_INGESTION_DATE = dbutils.widgets.get("STR_INGESTION_DATE")

INGESTION_DATE = datetime.strptime(STR_INGESTION_DATE, '%Y-%m-%d').date() if STR_INGESTION_DATE else date.today()

# COMMAND ----------

print('BRONZE_TB_RAW_INVENTARIO\t:', BRONZE_TB_RAW_INVENTARIO)
print('STR_INGESTION_DATE\t\t:', STR_INGESTION_DATE)
print('INGESTION_DATE\t\t\t:', INGESTION_DATE)

# COMMAND ----------

spark.sql(f"""
          CREATE OR REPLACE TEMPORARY VIEW nuevo_inventario
          AS
          SELECT *, current_timestamp() AS inserted_at FROM read_files(
              'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/productos/inventario/creado={INGESTION_DATE}',
              format => 'csv',
              header => true,
              inferSchema => true
              --schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
              )
          """)

# COMMAND ----------

spark.sql(f"""
    DELETE FROM {BRONZE_TB_RAW_INVENTARIO}
    WHERE creado = DATE('{INGESTION_DATE}')
""")

# COMMAND ----------

spark.sql(f"""
          INSERT INTO {BRONZE_TB_RAW_INVENTARIO}
          SELECT * FROM nuevo_inventario
          """)