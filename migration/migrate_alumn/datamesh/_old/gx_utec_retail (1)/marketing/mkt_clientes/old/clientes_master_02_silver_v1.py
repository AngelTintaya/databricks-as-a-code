# Databricks notebook source
# MAGIC %sql
# MAGIC /*
# MAGIC MERGE INTO g0_mkt_clientes.silver.clientes cli
# MAGIC USING g0_mkt_clientes.bronze.raw_clientes raw ON cli.cliente_id = raw.cliente_id
# MAGIC WHEN MATCHED THEN UPDATE SET
# MAGIC   cli.nombre = raw.nombre,
# MAGIC   cli.email = raw.email,
# MAGIC   cli.fecha_nacimiento = raw.fecha_nacimiento,
# MAGIC   cli.genero = raw.genero,
# MAGIC   cli.ciudad = raw.ciudad,
# MAGIC   cli.creado = raw.creado,
# MAGIC   cli.inserted_at = raw.inserted_at
# MAGIC WHEN NOT MATCHED THEN INSERT
# MAGIC   (cliente_id, nombre, email, fecha_nacimiento, genero, ciudad, creado, inserted_at)
# MAGIC VALUES
# MAGIC   (raw.cliente_id, raw.nombre, raw.email, raw.fecha_nacimiento, raw.genero, raw.ciudad, raw.created_at, current_timestamp())
# MAGIC */

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP MATERIALIZED VIEW IF EXISTS g0_mkt_clientes.silver.mv_clientes

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE MATERIALIZED VIEW g0_mkt_clientes.silver.mv_clientes
# MAGIC (
# MAGIC   cliente_id STRING COMMENT 'Identificador único del cliente',
# MAGIC   nombre STRING COMMENT 'Nombre del cliente',
# MAGIC   email STRING COMMENT 'Email del cliente',
# MAGIC   fecha_nacimiento DATE COMMENT 'Fecha de nacimiento del cliente',
# MAGIC   genero STRING COMMENT 'Género del cliente',
# MAGIC   ciudad STRING COMMENT 'Ciudad donde vive el cliente',
# MAGIC   created_at TIMESTAMP COMMENT 'Timestamp cuando el registro fue creado',
# MAGIC   inserted_at TIMESTAMP COMMENT 'Timestamp cuando el registro fue insertado'
# MAGIC )
# MAGIC COMMENT 'This materialized view contains cleaned and deduplicated client data'
# MAGIC AS
# MAGIC WITH rnk_cliente AS (
# MAGIC   SELECT
# MAGIC     cliente_id,
# MAGIC     INITCAP(nombre) AS nombre,
# MAGIC     email,
# MAGIC     fecha_nacimiento,
# MAGIC     genero,
# MAGIC     INITCAP(ubicacion) AS ciudad,
# MAGIC     CAST(creado AS TIMESTAMP) as created_at,
# MAGIC     inserted_at,
# MAGIC     ROW_NUMBER() OVER (PARTITION BY cliente_id ORDER BY inserted_at DESC) AS rnk
# MAGIC   FROM g0_mkt_clientes.bronze.raw_clientes
# MAGIC   WHERE 1 = 1
# MAGIC   AND cliente_id IS NOT NULL
# MAGIC   AND nombre IS NOT NULL
# MAGIC )
# MAGIC SELECT
# MAGIC   cliente_id,
# MAGIC   nombre,
# MAGIC   email,
# MAGIC   fecha_nacimiento,
# MAGIC   genero,
# MAGIC   ciudad,
# MAGIC   created_at,
# MAGIC   inserted_at
# MAGIC FROM rnk_cliente
# MAGIC WHERE rnk = 1

# COMMAND ----------

# MAGIC %sql
# MAGIC ALTER TABLE g0_mkt_clientes.silver.mv_clientes
# MAGIC ALTER COLUMN email SET TAGS ('PII');
# MAGIC
# MAGIC ALTER TABLE g0_mkt_clientes.silver.mv_clientes
# MAGIC ALTER COLUMN fecha_nacimiento SET TAGS ('PII');
# MAGIC
# MAGIC ALTER TABLE g0_mkt_clientes.silver.mv_clientes
# MAGIC ALTER COLUMN genero SET TAGS ('sensible');

# COMMAND ----------

# MAGIC %sql
# MAGIC REFRESH MATERIALIZED VIEW g0_mkt_clientes.silver.mv_clientes