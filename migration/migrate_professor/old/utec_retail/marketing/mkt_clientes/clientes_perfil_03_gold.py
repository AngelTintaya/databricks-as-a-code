# Databricks notebook source
# MAGIC %sql
# MAGIC DROP VIEW IF EXISTS g0_mkt_clientes.gold.vw_clientes_perfil

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW g0_mkt_clientes.gold.vw_clientes_perfil
# MAGIC COMMENT 'Vista que contiene el perfil del cliente'
# MAGIC AS
# MAGIC SELECT
# MAGIC   cliente_id,
# MAGIC   nombre,
# MAGIC   email,
# MAGIC   fecha_nacimiento,
# MAGIC   genero,
# MAGIC   ciudad,
# MAGIC   total_ventas,
# MAGIC   total_productos,
# MAGIC   cantidad_productos_comprados,
# MAGIC   total_monto,
# MAGIC   last_venta_id,
# MAGIC   last_producto_id,
# MAGIC   last_cantidad,
# MAGIC   last_monto_total,
# MAGIC   last_canal,
# MAGIC   inserted_at
# MAGIC FROM g0_mkt_clientes.silver.mv_clientes_perfil