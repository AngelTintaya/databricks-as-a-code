# Databricks notebook source
# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS g0_mkt_clientes.silver.clientes

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE g0_mkt_clientes.silver.clientes
# MAGIC (
# MAGIC   cliente_id STRING COMMENT 'Identificador único del cliente',
# MAGIC   nombre STRING COMMENT 'Nombre del cliente',
# MAGIC   email STRING COMMENT 'Email del cliente',
# MAGIC   fecha_nacimiento STRING COMMENT 'Fecha de nacimiento del cliente',
# MAGIC   genero STRING COMMENT 'Género del cliente',
# MAGIC   ciudad STRING COMMENT 'Ciudad donde vive el cliente',
# MAGIC   created_at TIMESTAMP COMMENT 'Timestamp cuando el registro fue creado',
# MAGIC   inserted_at TIMESTAMP COMMENT 'Timestamp cuando el registro fue insertado'
# MAGIC )
# MAGIC COMMENT 'Contiene información curada del cliente'
# MAGIC ;

# COMMAND ----------

# MAGIC %sql
# MAGIC ALTER TABLE g0_mkt_clientes.silver.clientes
# MAGIC ALTER COLUMN email SET TAGS ('PII');
# MAGIC
# MAGIC ALTER TABLE g0_mkt_clientes.silver.clientes
# MAGIC ALTER COLUMN fecha_nacimiento SET TAGS ('PII');
# MAGIC
# MAGIC ALTER TABLE g0_mkt_clientes.silver.clientes
# MAGIC ALTER COLUMN genero SET TAGS ('sensible');

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM g0_mkt_clientes.silver.clientes