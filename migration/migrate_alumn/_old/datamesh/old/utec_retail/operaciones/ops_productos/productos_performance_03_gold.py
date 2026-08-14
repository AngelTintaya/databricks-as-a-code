# Databricks notebook source
# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW g0_ops_productos.gold.vw_hm_producto_performance
# MAGIC COMMENT 'Vista histórica mensual que contiene el performance de cada producto'
# MAGIC AS
# MAGIC SELECT
# MAGIC   periodo,
# MAGIC   producto_id,
# MAGIC   producto_nombre,
# MAGIC   total_ventas,
# MAGIC   stock_actual,
# MAGIC   rotacion,
# MAGIC   ranking_rotacion,
# MAGIC   inserted_at
# MAGIC FROM g0_ops_productos.silver.hm_producto_performance

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW g0_ops_productos.gold.vw_um_producto_performance
# MAGIC COMMENT 'Vista del último mes que contiene el performance de cada producto'
# MAGIC AS
# MAGIC SELECT
# MAGIC   periodo,
# MAGIC   producto_id,
# MAGIC   producto_nombre,
# MAGIC   total_ventas,
# MAGIC   stock_actual,
# MAGIC   rotacion,
# MAGIC   ranking_rotacion,
# MAGIC   inserted_at
# MAGIC FROM g0_ops_productos.silver.mv_um_producto_performance