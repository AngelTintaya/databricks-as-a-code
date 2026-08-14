# Databricks notebook source
# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS g0_ops_productos.silver.hm_producto_performance

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE g0_ops_productos.silver.hm_producto_performance (
# MAGIC   periodo STRING COMMENT 'Periodo de tiempo mensual en el que se calculó el performance',
# MAGIC   producto_id STRING COMMENT 'Identificador único del producto',
# MAGIC   producto_nombre STRING COMMENT 'Nombre del producto',
# MAGIC   total_ventas INT COMMENT 'Total de unidades vendidas en el periodo',
# MAGIC   stock_actual INT COMMENT 'Stock actual al cierre del periodo',
# MAGIC   rotacion DOUBLE COMMENT 'Ratio de rotación del producto en el periodo calculado como total_ventas / stock_actual.',
# MAGIC   ranking_rotacion INT COMMENT 'Ranking dentro del mes por rotación, orden descendente.',
# MAGIC   inserted_at TIMESTAMP COMMENT 'Timestamp en que se insertó este snapshot'
# MAGIC )
# MAGIC COMMENT 'Tabla histórica mensual con indicadores de performance de productos'
# MAGIC CLUSTER BY (periodo, producto_id)
# MAGIC ;

# COMMAND ----------

# MAGIC %sql
# MAGIC OPTIMIZE g0_ops_productos.silver.hm_producto_performance