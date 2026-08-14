# Databricks notebook source
my_catalog = 'g204_cmc_demanda_zonal'

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {my_catalog}.silver.vw_ventas
    AS
    SELECT
        venta_id,
        cliente_id,
        dark_store_id,
        distrito_dark_store,
        fecha_venta,
        hora_venta,
        categoria_producto,
        producto,
        cantidad,
        precio_unitario,
        monto_total,
        metodo_pago,
        canal,
        inserted_at
    FROM {my_catalog}.bronze.raw_ventas_darkstore
    """
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {my_catalog}.silver.vw_envios_geo
    AS
    SELECT 
        v.venta_id,
        v.cliente_id,
        v.producto,
        v.categoria_producto,
        v.fecha_venta,
        v.cantidad,
        v.monto_total,
        e.envio_id,
        e.distrito_entrega AS zona_id,
        e.estado_entrega,            
        e.tiempo_entrega_min,
        e.distancia_km,
        current_timestamp() AS updated_at
    FROM {my_catalog}.silver.vw_ventas v
    INNER JOIN {my_catalog}.bronze.raw_envios e
    ON v.venta_id = e.venta_id
    """
)