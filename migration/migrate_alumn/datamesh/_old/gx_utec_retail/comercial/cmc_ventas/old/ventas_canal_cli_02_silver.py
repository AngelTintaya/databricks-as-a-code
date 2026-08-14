# Databricks notebook source
# MAGIC %sql
# MAGIC DROP MATERIALIZED VIEW IF EXISTS g0_cmc_ventas.silver.mv_ventas_canal_por_cliente

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE MATERIALIZED VIEW g0_cmc_ventas.silver.mv_ventas_canal_por_cliente
# MAGIC (
# MAGIC   cod_mes STRING COMMENT 'Código del mes en que se realizó la venta en formato YYYYMM',
# MAGIC   cliente_id STRING COMMENT 'Identificador único del cliente',
# MAGIC   fecha_venta DATE COMMENT 'Fecha en que se realizó la venta',
# MAGIC   canal STRING COMMENT 'Canal por el que se realizó la venta',
# MAGIC   numero_ventas INTEGER COMMENT 'Cantidad de productos vendidos',
# MAGIC   monto_total DOUBLE COMMENT 'Monto total de venta',
# MAGIC   prev_fecha_venta DATE COMMENT 'Fecha de la venta previa',
# MAGIC   prev_canal STRING COMMENT 'Canal de la venta previa',
# MAGIC   prev_numero_ventas INTEGER COMMENT 'Cantidad de productos vendidos en la venta previa',
# MAGIC   prev_monto_total DOUBLE COMMENT 'Monto total de la venta previa',
# MAGIC   dias_venta_diferencia INTEGER COMMENT 'Diferencia de días entre fecha_venta y prev_fecha_venta',
# MAGIC   inserted_at TIMESTAMP COMMENT 'Timestamp en que se actualizó el registro'
# MAGIC )
# MAGIC COMMENT 'Vista materializada que contiene un resumen de ventas por canal para cada cliente, incluyendo comparaciones detalladas con la venta anterior.'
# MAGIC AS
# MAGIC WITH ventas_por_canal AS (
# MAGIC   SELECT
# MAGIC     v.cod_mes,
# MAGIC     v.cliente_id,
# MAGIC     v.canal,
# MAGIC     v.fecha_venta,
# MAGIC     CAST(SUM(v.cantidad) AS INTEGER) AS numero_ventas,
# MAGIC     SUM(v.monto_total) AS monto_total
# MAGIC   FROM g0_cmc_ventas.gold.vw_ventas v
# MAGIC   GROUP BY
# MAGIC     v.cod_mes,
# MAGIC     v.cliente_id,
# MAGIC     v.canal,
# MAGIC     v.fecha_venta
# MAGIC ),
# MAGIC ventas_con_prev AS (
# MAGIC   SELECT
# MAGIC     *,
# MAGIC     LAG(fecha_venta) OVER (PARTITION BY cliente_id ORDER BY fecha_venta DESC) AS prev_fecha_venta
# MAGIC   FROM ventas_por_canal
# MAGIC )
# MAGIC SELECT
# MAGIC   cur.cod_mes,
# MAGIC   cur.cliente_id,
# MAGIC   cur.fecha_venta,
# MAGIC   cur.canal,
# MAGIC   cur.numero_ventas,
# MAGIC   cur.monto_total,
# MAGIC   prev.fecha_venta AS prev_fecha_venta,
# MAGIC   prev.canal AS prev_canal,
# MAGIC   prev.numero_ventas AS prev_numero_ventas,
# MAGIC   prev.monto_total AS prev_monto_total,
# MAGIC   DATEDIFF(cur.fecha_venta, prev.fecha_venta) AS dias_venta_diferencia,
# MAGIC   CURRENT_TIMESTAMP() AS inserted_at
# MAGIC FROM ventas_por_canal cur
# MAGIC LEFT JOIN ventas_con_prev prev
# MAGIC   ON cur.cliente_id = prev.cliente_id
# MAGIC   AND cur.fecha_venta = prev.prev_fecha_venta
# MAGIC ORDER BY cur.cliente_id, cur.fecha_venta ASC

# COMMAND ----------

# MAGIC %md
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC REFRESH MATERIALIZED VIEW g0_cmc_ventas.silver.mv_ventas_canal_por_cliente