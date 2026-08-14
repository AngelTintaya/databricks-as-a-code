# Databricks notebook source
my_catalog = 'gx_catalog'
my_prefix = 'atm'

# COMMAND ----------

table_input = f'{my_catalog}.default.{my_prefix}_basic_input'
table_transform = f'{my_catalog}.default.{my_prefix}_basic_transform'
table_summary = f'{my_catalog}.default.{my_prefix}_basic_summary'

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {table_input}
    AS
    SELECT *, current_timestamp() AS inserted_at
    FROM read_files(
        'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/input.csv',
        format => 'csv',
        header => true,
        inferSchema => true,
        ignoreLeadingWhiteSpace => true,
        ignoreTrailingWhiteSpace => true
        -- schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
    )
    """
)

# COMMAND ----------

spark.sql(f'SELECT * FROM {table_input}').display()

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {table_transform} AS 
    SELECT
        inp.id,
        inp.producto,
        inp.cantidad,
        inp.precio,
        inp.inserted_at,
        inp.cantidad * inp.precio AS total
    FROM {table_input} inp
    WHERE inp.id IS NOT NULL    
    """
)


# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {table_summary}
    AS
    SELECT
        producto,
        SUM(total) AS total_sum
    FROM {table_transform}
    GROUP BY producto
    """
)

# COMMAND ----------

spark.sql(f"SELECT * FROM {table_summary}").display()