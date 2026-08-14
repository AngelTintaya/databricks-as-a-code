# Databricks notebook source
# DBTITLE 1,Load parameters
# MAGIC %run ./config/parameters

# COMMAND ----------

# DBTITLE 1,Resolve parameters
CATALOG = params['catalog']
PREFIX  = params['prefix']

table_silver = f'{CATALOG}.silver.{PREFIX}_sql_pro_transform'
table_gold   = f'{CATALOG}.gold.{PREFIX}_sql_pro_summary'

print(f'Source : {table_silver}')
print(f'Target : {table_gold}')

# COMMAND ----------

# DBTITLE 1,Build summary (always full recalculation)
spark.sql(
    f"""
    CREATE OR REPLACE TABLE {table_gold} AS
    SELECT
        producto,
        SUM(total)    AS total_sum,
        SUM(cantidad) AS total_unidades,
        COUNT(*)      AS num_transacciones,
        current_timestamp() AS calculated_at
    FROM {table_silver}
    GROUP BY producto
    """
)

# COMMAND ----------

# DBTITLE 1,Validate: no negative or zero totals
spark.sql(
    f"""
    SELECT
        CASE WHEN COUNT(*) > 0
             THEN raise_error('Negative or zero total_sum in ' || COUNT(*) || ' products — check silver data')
             ELSE 'OK: all product totals are positive'
        END AS resultado
    FROM {table_gold}
    WHERE total_sum <= 0
    """
).display()

# COMMAND ----------

# DBTITLE 1,Validate output
spark.sql(f"SELECT * FROM {table_gold} ORDER BY total_sum DESC").display()