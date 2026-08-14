# Databricks notebook source
my_catalog = 'gx_catalog'
my_prefix = 'atm'

# COMMAND ----------

table_bronze = f'{my_catalog}.bronze.{my_prefix}_sql_input'

# COMMAND ----------

spark.sql(f"""DROP TABLE IF EXISTS {table_bronze}""")

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {table_bronze} AS
    SELECT *, current_timestamp() AS inserted_at
    FROM read_files(
        'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/input.csv',
        format => 'csv',
        header => true,
        -- inferSchema => true,
        schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
    )    
    """
)

# COMMAND ----------

spark.sql(
    f"""
    SELECT
        CASE WHEN COUNT(*) > 0 THEN raise_error('ID is null')
            ELSE 'Datos validados: No hay ID nulos'
        END AS resultados
    FROM {table_bronze}
    WHERE id IS NULL
    """
).display()

# COMMAND ----------

# spark.sql(f"""SELECT * FROM {table_bronze}""").display()