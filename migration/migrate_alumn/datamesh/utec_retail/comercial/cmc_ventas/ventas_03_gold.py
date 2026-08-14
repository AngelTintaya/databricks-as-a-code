# Databricks notebook source
my_catalog = 'gx05_cmc_ventas'

# COMMAND ----------

spark.sql(f"""DROP VIEW IF EXISTS {my_catalog}.gold.vw_ventas""")
spark.sql(f"""DROP VIEW IF EXISTS {my_catalog}.gold.vw_ventas_por_canal""")
spark.sql(f"""DROP VIEW IF EXISTS {my_catalog}.gold.vw_ventas_por_producto""")

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {my_catalog}.gold.vw_ventas
    COMMENT 'Esta vista contiene detalles de ventas'
    AS
    SELECT
        cod_mes,
        venta_id,
        cliente_id,
        producto_id,
        fecha_venta,
        cantidad,
        monto_total,
        canal,
        created_at,
        inserted_at
    FROM {my_catalog}.silver.mv_ventas
    """
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {my_catalog}.gold.vw_ventas_por_canal
    (
        cod_mes,
        fecha_venta, -- COMMENT 'Fecha en que se realizó la venta',
        canal, -- COMMENT 'Canal por el que se realizó la venta',
        total_productos COMMENT 'Cantidad de productos vendidos',
        total_monto COMMENT 'Monto total vendido'
    )
    COMMENT 'Vista que contiene el consolidado de ventas'
    AS
    SELECT
        cod_mes,
        fecha_venta,
        canal,
        SUM(cantidad) AS total_productos,
        SUM(monto_total) AS total_monto
    FROM {my_catalog}.gold.vw_ventas
    GROUP BY
        cod_mes,
        fecha_venta,
        canal
    """
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {my_catalog}.gold.vw_ventas_por_producto
    (
        cod_mes COMMENT 'View - Código del mes en que se realizó la venta en formato YYYYMM',
        fecha_venta COMMENT 'View - Fecha en que se realizó la venta',
        producto_id COMMENT 'View - Identificador único del producto',
        total_productos COMMENT 'Cantidad de productos vendidos',
        total_monto COMMENT 'Monto total vendido'
    )
    COMMENT 'Vista que contiene el consolidado de ventas'
    AS
    SELECT
        cod_mes,
        fecha_venta,
        producto_id,
        SUM(cantidad) AS total_productos,
        SUM(monto_total) AS total_monto
    FROM {my_catalog}.gold.vw_ventas
    GROUP BY
        cod_mes,
        fecha_venta,
        producto_id
    """
)