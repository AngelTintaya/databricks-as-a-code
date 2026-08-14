# Databricks notebook source
my_catalog = 'g204_cmc_demanda_zonal'

# COMMAND ----------

spark.sql(f"""DROP VIEW IF EXISTS {my_catalog}.gold.vw_top_productos_zona""")
spark.sql(f"""DROP VIEW IF EXISTS {my_catalog}.gold.vw_probabilidad_compra""")

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {my_catalog}.gold.vw_top_productos_zona
    COMMENT 'Data Product que expone el ranking de productos más demandados por mes y zona'
    AS
    SELECT
        cod_mes,
        zona_id ,
        producto,
        total_ventas_zona,
        monto_total_zona,
        ROW_NUMBER() OVER (PARTITION BY cod_mes, zona_id ORDER BY total_ventas_zona DESC) AS ranking_posicion
    FROM {my_catalog}.silver.mv_demanda_zonal
    """
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {my_catalog}.gold.vw_probabilidad_compra
    COMMENT 'Data Product:Reporte que mide qué tan bien se entregan los pedidos y qué porcentaje del total de la zona representa cada producto'
    AS
    SELECT
        cod_mes,
        zona_id,
        producto,
        total_ventas_zona,
        envios_completados,
        ROUND((CAST(envios_completados AS DOUBLE) / NULLIF(total_ventas_zona, 0)), 4) AS porcentaje_envios_entregados,
        ROUND((monto_total_zona / SUM(monto_total_zona) OVER(PARTITION BY cod_mes, zona_id)), 4) AS porcentaje_ventas_distrito
    FROM {my_catalog}.silver.mv_demanda_zonal
    """
)