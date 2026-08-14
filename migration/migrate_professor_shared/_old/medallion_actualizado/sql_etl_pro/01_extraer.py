# Databricks notebook source
# DBTITLE 1,Load parameters
# MAGIC %run ./config/parameters

# COMMAND ----------

# DBTITLE 1,Resolve parameters
CATALOG     = params['catalog']
PREFIX      = params['prefix']
SOURCE_PATH = params['source_path']

table_bronze = f'{CATALOG}.bronze.{PREFIX}_sql_pro_input'

print(f'Source : {SOURCE_PATH}')
print(f'Target : {table_bronze}')

# COMMAND ----------

# DBTITLE 1,Load source into staging view
spark.sql(
    f"""
    CREATE OR REPLACE TEMP VIEW vw_bronze_staging AS
    SELECT
        id,
        producto,
        cantidad,
        precio,
        current_timestamp() AS inserted_at
    FROM read_files(
        '{SOURCE_PATH}',
        format => 'csv',
        header => true,
        schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
    )
    """
)

# COMMAND ----------

# DBTITLE 1,Validate: row count > 0
spark.sql(
    """
    SELECT
        CASE WHEN COUNT(*) = 0
             THEN raise_error('Source file is empty — no rows loaded')
             ELSE 'OK: ' || COUNT(*) || ' rows found in source'
        END AS resultado
    FROM vw_bronze_staging
    """
).display()

# COMMAND ----------

# DBTITLE 1,Report: data quality issues found
spark.sql(
    """
    SELECT
        COUNT(*) FILTER (WHERE id IS NULL)       AS null_id,
        COUNT(*) FILTER (WHERE producto IS NULL) AS null_producto,
        COUNT(*) FILTER (WHERE precio IS NULL)   AS null_precio,
        COUNT(*) FILTER (WHERE precio < 0)       AS negative_precio,
        COUNT(*) FILTER (WHERE cantidad <= 0)    AS zero_or_neg_cantidad
    FROM vw_bronze_staging
    """
).display()

# COMMAND ----------

# DBTITLE 1,Write bronze (full reload — exact copy of source)
spark.sql(
    f"""
    CREATE OR REPLACE TABLE {table_bronze} AS
    SELECT * FROM vw_bronze_staging
    """
)

# COMMAND ----------

# DBTITLE 1,Validate load
spark.sql(f"SELECT COUNT(*) AS total_rows FROM {table_bronze}").display()