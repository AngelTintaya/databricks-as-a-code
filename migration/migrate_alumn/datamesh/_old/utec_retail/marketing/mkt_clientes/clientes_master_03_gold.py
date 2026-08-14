# Databricks notebook source
# MAGIC %sql
# MAGIC DROP VIEW IF EXISTS g0_mkt_clientes.gold.vw_clientes

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW g0_mkt_clientes.gold.vw_clientes
# MAGIC COMMENT 'Vista que contiene información curada de clientes'
# MAGIC AS
# MAGIC SELECT
# MAGIC   cliente_id,
# MAGIC   nombre,
# MAGIC   email,
# MAGIC   fecha_nacimiento,
# MAGIC   genero,
# MAGIC   ciudad,
# MAGIC   created_at,
# MAGIC   inserted_at
# MAGIC FROM g0_mkt_clientes.silver.mv_clientes