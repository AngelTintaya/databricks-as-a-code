# Databricks notebook source
my_catalog = 'gx05_cmc_ventas'

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {my_catalog}.silver.vw_ventas
    AS
    SELECT
        venta_id,
        cliente_id,
        producto_id,
        fecha_venta,
        cantidad,
        monto_total,
        lower(canal) AS canal,
        fecha,
        inserted_at
    FROM {my_catalog}.bronze.raw_ventas_ecommerce
    UNION ALL
    SELECT
        venta_id,
        cliente_id,
        producto_id,
        fecha_venta,
        cantidad,
        monto_total,
        'tienda' AS canal,
        fecha,
        inserted_at
    FROM {my_catalog}.bronze.raw_ventas_tienda
    """
)