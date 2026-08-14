# Databricks notebook source
# MAGIC %sql
# MAGIC DROP VIEW IF EXISTS g0_ops_productos.gold.vw_inventario

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW g0_ops_productos.gold.vw_inventario
# MAGIC COMMENT 'Vista que contiene información del inventario'
# MAGIC AS
# MAGIC SELECT
# MAGIC   cod_mes,
# MAGIC   producto_id,
# MAGIC   producto_nombre,
# MAGIC   stock,
# MAGIC   sede,
# MAGIC   created_at,
# MAGIC   inserted_at
# MAGIC FROM g0_ops_productos.silver.mv_inventario