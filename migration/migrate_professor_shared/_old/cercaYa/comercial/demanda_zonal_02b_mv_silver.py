# Databricks notebook source
# MAGIC %md
# MAGIC # Cluster Compute

# COMMAND ----------

my_catalog = 'g204_cmc_demanda_zonal'

# COMMAND ----------

dbutils.widgets.text('SILVER_MV_DEMANDA_ZONAL', f'{my_catalog}.silver.mv_demanda_zonal')

# COMMAND ----------

# MAGIC %md
# MAGIC # SQL Warehouse Compute

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP MATERIALIZED VIEW IF EXISTS IDENTIFIER(:SILVER_MV_DEMANDA_ZONAL)

# COMMAND ----------

# DBTITLE 1,Celda 6
# MAGIC %sql
# MAGIC CREATE OR REPLACE MATERIALIZED VIEW g204_cmc_demanda_zonal.silver.mv_demanda_zonal
# MAGIC (
# MAGIC     cod_mes COMMENT 'Código del mes en formato YYYYMM extraído de la fecha de venta',
# MAGIC     zona_id COMMENT 'Distrito geográfico de entrega',
# MAGIC     producto COMMENT 'Nombre específico del producto vendido',
# MAGIC     total_ventas_zona COMMENT 'Cantidad física total de productos vendidos en la zona',
# MAGIC     monto_total_zona COMMENT 'Monto económico total acumulado en la zona',
# MAGIC     envios_completados COMMENT 'Total de envíos con estado exitoso (Entregado)',
# MAGIC     created_at COMMENT 'Timestamp de creación del registro analítico'
# MAGIC )
# MAGIC COMMENT 'Vista materializada que contiene el consolidado analítico de demanda zonal y envíos'
# MAGIC AS
# MAGIC SELECT
# MAGIC     DATE_FORMAT(fecha_venta, 'yyyyMM') AS cod_mes,
# MAGIC     zona_id,
# MAGIC     producto,
# MAGIC     SUM(cantidad) AS total_ventas_zona,
# MAGIC     SUM(monto_total) AS monto_total_zona,
# MAGIC     COUNT(DISTINCT CASE WHEN LOWER(estado_entrega) = 'entregado' THEN envio_id END)::INT AS envios_completados,
# MAGIC     CURRENT_TIMESTAMP() AS created_at
# MAGIC FROM g204_cmc_demanda_zonal.silver.vw_envios_geo
# MAGIC GROUP BY 
# MAGIC     DATE_FORMAT(fecha_venta, 'yyyyMM'),
# MAGIC     zona_id,
# MAGIC     producto

# COMMAND ----------

# MAGIC %sql
# MAGIC REFRESH MATERIALIZED VIEW IDENTIFIER(:SILVER_MV_DEMANDA_ZONAL)