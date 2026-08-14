# Databricks notebook source
from datetime import datetime, date

# COMMAND ----------

# dbutils.widgets.text('STR_INGESTION_DATE', '2024-01-01')

# COMMAND ----------

STR_INGESTION_DATE = dbutils.widgets.get("STR_INGESTION_DATE")
INGESTION_DATE = datetime.strptime(STR_INGESTION_DATE, '%Y-%m-%d').date() if STR_INGESTION_DATE else date.today()
# INGESTION_TIMESTAMP = datetime.strptime(STR_INGESTION_DATE, '%Y-%m-%d') if STR_INGESTION_DATE else datetime.now()

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

spark.sql("""
          INSERT INTO g0_ops_productos.bronze.raw_inventario
          SELECT * FROM nuevo_inventario
          """)