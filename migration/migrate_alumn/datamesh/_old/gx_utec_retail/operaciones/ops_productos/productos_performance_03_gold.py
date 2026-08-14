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
# MAGIC (
# MAGIC   periodo COMMENT 'Periodo de tiempo mensual en el que se calculó el performance',
# MAGIC   producto_id COMMENT 'Identificador único del producto',
# MAGIC   producto_nombre COMMENT 'Nombre del producto',
# MAGIC   total_ventas COMMENT 'Total de unidades vendidas en el periodo',
# MAGIC   stock_actual COMMENT 'Stock actual al cierre del periodo',
# MAGIC   rotacion COMMENT 'Ratio de rotación del producto en el periodo calculado como total_ventas / stock_actual.',
# MAGIC   ranking_rotacion COMMENT 'Ranking dentro del mes por rotación, orden descendente.',
# MAGIC   inserted_at COMMENT 'Timestamp en que se insertó este snapshot'
# MAGIC )
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
# MAGIC FROM g0_ops_productos.silver.um_producto_performance