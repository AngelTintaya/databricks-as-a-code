# Databricks notebook source
# MAGIC %sql
# MAGIC DROP VIEW IF EXISTS g0_mkt_clientes.gold.vw_clientes

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW g0_mkt_clientes.gold.vw_clientes
# MAGIC (
# MAGIC   cliente_id,
# MAGIC   nombre,
# MAGIC   email COMMENT 'Email del cliente',
# MAGIC   fecha_nacimiento COMMENT 'Fecha de nacimiento del cliente',
# MAGIC   genero COMMENT 'Género del cliente',
# MAGIC   ciudad,
# MAGIC   created_at,
# MAGIC   inserted_at
# MAGIC )
# MAGIC COMMENT 'Vista que contiene información curada de clientes'
# MAGIC AS
# MAGIC SELECT
# MAGIC   cliente_id,
# MAGIC   nombre,
# MAGIC   g0_catalog.default.pii_mask(email) AS email,
# MAGIC   g0_catalog.default.pii_col(fecha_nacimiento) AS fecha_nacimiento,
# MAGIC   g0_catalog.default.pii_mask(genero) AS genero,
# MAGIC   ciudad,
# MAGIC   created_at,
# MAGIC   inserted_at
# MAGIC FROM g0_mkt_clientes.silver.clientes