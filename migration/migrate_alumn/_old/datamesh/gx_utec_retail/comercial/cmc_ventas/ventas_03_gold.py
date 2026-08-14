# Databricks notebook source
# MAGIC %sql
# MAGIC DROP VIEW IF EXISTS g0_cmc_ventas.gold.vw_ventas;
# MAGIC DROP VIEW IF EXISTS g0_cmc_ventas.gold.vw_ventas_por_canal;
# MAGIC DROP VIEW IF EXISTS g0_cmc_ventas.gold.vw_ventas_por_producto;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW g0_cmc_ventas.gold.vw_ventas
# MAGIC COMMENT 'Esta vista contiene detalles de ventas'
# MAGIC AS
# MAGIC SELECT
# MAGIC   cod_mes,
# MAGIC   venta_id,
# MAGIC   cliente_id,
# MAGIC   producto_id,
# MAGIC   fecha_venta,
# MAGIC   cantidad,
# MAGIC   monto_total,
# MAGIC   canal,
# MAGIC   created_at,
# MAGIC   inserted_at
# MAGIC FROM g0_cmc_ventas.silver.mv_ventas

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW g0_cmc_ventas.gold.vw_ventas_por_canal
# MAGIC (
# MAGIC   cod_mes,
# MAGIC   fecha_venta, -- COMMENT 'Fecha en que se realizó la venta',
# MAGIC   canal, -- COMMENT 'Canal por el que se realizó la venta',
# MAGIC   total_productos COMMENT 'Cantidad de productos vendidos',
# MAGIC   total_monto COMMENT 'Monto total vendido'
# MAGIC )
# MAGIC COMMENT 'Vista que contiene el consolidado de ventas'
# MAGIC AS
# MAGIC SELECT
# MAGIC   cod_mes,
# MAGIC   fecha_venta,
# MAGIC   canal,
# MAGIC   SUM(cantidad) AS total_productos,
# MAGIC   SUM(monto_total) AS total_monto
# MAGIC FROM g0_cmc_ventas.gold.vw_ventas
# MAGIC GROUP BY
# MAGIC   cod_mes,
# MAGIC   fecha_venta,
# MAGIC   canal

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW g0_cmc_ventas.gold.vw_ventas_por_producto
# MAGIC (
# MAGIC   cod_mes COMMENT 'View - Código del mes en que se realizó la venta en formato YYYYMM',
# MAGIC   fecha_venta COMMENT 'View - Fecha en que se realizó la venta',
# MAGIC   producto_id COMMENT 'View - Identificador único del producto',
# MAGIC   total_productos COMMENT 'Cantidad de productos vendidos',
# MAGIC   total_monto COMMENT 'Monto total vendido'
# MAGIC )
# MAGIC COMMENT 'Vista que contiene el consolidado de ventas'
# MAGIC AS
# MAGIC SELECT
# MAGIC   cod_mes,
# MAGIC   fecha_venta,
# MAGIC   producto_id,
# MAGIC   SUM(cantidad) AS total_productos,
# MAGIC   SUM(monto_total) AS total_monto
# MAGIC FROM g0_cmc_ventas.gold.vw_ventas
# MAGIC GROUP BY
# MAGIC   cod_mes,
# MAGIC   fecha_venta,
# MAGIC   producto_id