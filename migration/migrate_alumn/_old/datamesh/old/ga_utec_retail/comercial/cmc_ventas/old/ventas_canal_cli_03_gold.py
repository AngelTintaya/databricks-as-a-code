# Databricks notebook source
# MAGIC %sql
# MAGIC DROP VIEW IF EXISTS g0_cmc_ventas.gold.vw_ventas_canal_por_cliente;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW g0_cmc_ventas.gold.vw_ventas_canal_por_cliente
# MAGIC COMMENT 'Esta vista contiene un resumen de ventas por canal para cada cliente, incluyendo comparaciones detalladas con la venta anterior.'
# MAGIC AS
# MAGIC SELECT
# MAGIC   cod_mes,
# MAGIC   cliente_id,
# MAGIC   fecha_venta,
# MAGIC   canal,
# MAGIC   numero_ventas,
# MAGIC   monto_total,
# MAGIC   prev_fecha_venta,
# MAGIC   prev_canal,
# MAGIC   prev_numero_ventas,
# MAGIC   prev_monto_total,
# MAGIC   dias_venta_diferencia,
# MAGIC   inserted_at
# MAGIC FROM g0_cmc_ventas.silver.mv_ventas_canal_por_cliente