# Databricks notebook source
# MAGIC %sql
# MAGIC DROP MATERIALIZED VIEW IF EXISTS g0_ops_productos.silver.mv_inventario

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE MATERIALIZED VIEW g0_ops_productos.silver.mv_inventario
# MAGIC (
# MAGIC   cod_mes STRING COMMENT 'Mes en el que se hizo el inventario',
# MAGIC   producto_id STRING COMMENT 'Identificador único del producto',
# MAGIC   producto_nombre STRING COMMENT 'Nombre del producto',
# MAGIC   stock INTEGER COMMENT 'Stock disponible',
# MAGIC   sede STRING COMMENT 'Sede en la cual hace referencia el inventario',
# MAGIC   created_at TIMESTAMP COMMENT 'Timestamp en que se creó el registro',
# MAGIC   inserted_at TIMESTAMP COMMENT 'Timestamp en que se insertó el registro'
# MAGIC )
# MAGIC COMMENT 'Esta vista materializada contiene datos del inventario'
# MAGIC AS
# MAGIC WITH rnk_producto AS (
# MAGIC   SELECT
# MAGIC     CAST(codmes AS STRING) AS cod_mes,
# MAGIC     producto_id,
# MAGIC     INITCAP(producto_nombre) AS producto_nombre,
# MAGIC     stock,
# MAGIC     INITCAP(tienda) as sede,
# MAGIC     CAST(creado AS TIMESTAMP) as created_at,
# MAGIC     inserted_at,
# MAGIC     ROW_NUMBER() OVER (PARTITION BY codmes, producto_id ORDER BY inserted_at DESC) AS rnk
# MAGIC   FROM g0_ops_productos.bronze.raw_inventario
# MAGIC   WHERE 1 = 1
# MAGIC   AND producto_id IS NOT NULL
# MAGIC   AND producto_nombre IS NOT NULL
# MAGIC )
# MAGIC SELECT
# MAGIC     cod_mes,
# MAGIC     producto_id,
# MAGIC     producto_nombre,
# MAGIC     stock,
# MAGIC     sede,
# MAGIC     created_at,
# MAGIC     inserted_at
# MAGIC FROM rnk_producto
# MAGIC WHERE rnk = 1

# COMMAND ----------

# MAGIC %sql
# MAGIC REFRESH MATERIALIZED VIEW g0_ops_productos.silver.mv_inventario