# Databricks notebook source
# DBTITLE 1,Load parameters
# MAGIC %run ./config/parameters

# COMMAND ----------

# DBTITLE 1,Resolve parameters
CATALOG = params['catalog']
PREFIX  = params['prefix']

table_bronze     = f'{CATALOG}.bronze.{PREFIX}_sql_pro_input'
table_silver     = f'{CATALOG}.silver.{PREFIX}_sql_pro_transform'
table_quarantine = f'{CATALOG}.silver.{PREFIX}_sql_pro_quarantine'

print(f'Source     : {table_bronze}')
print(f'Target     : {table_silver}')
print(f'Quarantine : {table_quarantine}')

# COMMAND ----------

# DBTITLE 1,Configure widget
dbutils.widgets.text("descuento", "0.1")

# COMMAND ----------

# DBTITLE 1,Resolve widget
DISCOUNT   = float(dbutils.widgets.get("descuento"))
MULTIPLIER = 1 - DISCOUNT

print(f'Descuento  : {DISCOUNT}')
print(f'Multiplier : {MULTIPLIER}')

# COMMAND ----------

# DBTITLE 1,Create silver table if not exists
spark.sql(
    f"""
    CREATE TABLE IF NOT EXISTS {table_silver} (
        id           INT,
        producto     STRING,
        cantidad     INT,
        precio       DOUBLE,
        descuento    DOUBLE,
        total        DOUBLE,
        inserted_at  TIMESTAMP,
        processed_at TIMESTAMP
    )
    USING DELTA
    """
)

# COMMAND ----------

# DBTITLE 1,Build clean staging view
spark.sql(
    f"""
    CREATE OR REPLACE TEMP VIEW vw_silver_staging AS
    SELECT
        id,
        producto,
        cantidad,
        precio,
        {DISCOUNT}                          AS descuento,
        cantidad * precio * {MULTIPLIER}    AS total,
        inserted_at,
        current_timestamp()                 AS processed_at
    FROM {table_bronze}
    WHERE producto IS NOT NULL
      AND precio   IS NOT NULL
      AND precio    > 0
      AND cantidad  > 0
    """
)

# COMMAND ----------

# DBTITLE 1,Build quarantine staging view (bad records with rejection reason)
spark.sql(
    f"""
    CREATE OR REPLACE TEMP VIEW vw_quarantine_staging AS
    SELECT
        id,
        producto,
        cantidad,
        precio,
        inserted_at,
        array_join(
            array(
                CASE WHEN producto IS NULL THEN 'null_producto'        END,
                CASE WHEN precio   IS NULL THEN 'null_precio'          END,
                CASE WHEN precio    < 0    THEN 'negative_precio'      END,
                CASE WHEN cantidad <= 0    THEN 'zero_or_neg_cantidad' END
            ),
            ', '
        )                   AS rejection_reason,
        current_timestamp() AS quarantined_at
    FROM {table_bronze}
    WHERE producto IS NULL
       OR precio   IS NULL
       OR precio    < 0
       OR cantidad <= 0
    """
)

# COMMAND ----------

# DBTITLE 1,Report: clean vs quarantined
spark.sql(
    f"""
    SELECT
        (SELECT COUNT(*) FROM {table_bronze})        AS bronze_rows,
        (SELECT COUNT(*) FROM vw_silver_staging)     AS clean_rows,
        (SELECT COUNT(*) FROM vw_quarantine_staging) AS quarantined_rows
    """
).display()

# COMMAND ----------

# DBTITLE 1,Merge into silver (upsert clean records, remove records that became bad)
spark.sql(
    f"""
    MERGE INTO {table_silver} AS target
    USING vw_silver_staging   AS source
        ON target.id = source.id
    WHEN MATCHED THEN
        UPDATE SET
            target.producto     = source.producto,
            target.cantidad     = source.cantidad,
            target.precio       = source.precio,
            target.descuento    = source.descuento,
            target.total        = source.total,
            target.inserted_at  = source.inserted_at,
            target.processed_at = source.processed_at
    WHEN NOT MATCHED THEN
        INSERT (id, producto, cantidad, precio, descuento, total, inserted_at, processed_at)
        VALUES (source.id, source.producto, source.cantidad, source.precio,
                source.descuento, source.total, source.inserted_at, source.processed_at)
    WHEN NOT MATCHED BY SOURCE THEN DELETE
    """
).display()

# COMMAND ----------

# DBTITLE 1,Write quarantine (full snapshot of currently bad records)
spark.sql(
    f"""
    CREATE OR REPLACE TABLE {table_quarantine} AS
    SELECT * FROM vw_quarantine_staging
    """
)

# COMMAND ----------

# DBTITLE 1,Show quarantined records
spark.sql(f"SELECT * FROM {table_quarantine} ORDER BY id").display()

# COMMAND ----------

# DBTITLE 1,Validate silver output
spark.sql(f"SELECT * FROM {table_silver} ORDER BY id").display()