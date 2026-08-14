# Databricks notebook source
my_catalog = 'g204_cmc_demanda_zonal'

# COMMAND ----------

spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.bronze.raw_ventas_darkstore""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.bronze.raw_envios""")

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {my_catalog}.bronze.raw_ventas_darkstore
    AS
    SELECT *, current_timestamp() AS inserted_at
    FROM read_files(
        'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow2/G04/comercial/',
        format => 'csv',
        header => true,
        inferSchema => true
        --schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
        )
    """
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {my_catalog}.bronze.raw_envios
    AS
    SELECT *, current_timestamp() AS inserted_at
    FROM read_files(
        'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow2/G04/operaciones/',
        format => 'csv',
        header => true,
        inferSchema => true
        --schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
        )
    """
)