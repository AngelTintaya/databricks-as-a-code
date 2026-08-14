# Databricks notebook source
# MAGIC %sql
# MAGIC DROP MATERIALIZED VIEW IF EXISTS g0_mkt_clientes.silver.mv_clientes_perfil

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE MATERIALIZED VIEW g0_mkt_clientes.silver.mv_clientes_perfil
# MAGIC (
# MAGIC   cliente_id STRING COMMENT 'Identificador único del cliente',
# MAGIC   nombre STRING COMMENT 'Nombre del cliente',
# MAGIC   email STRING COMMENT 'Email del cliente',
# MAGIC   fecha_nacimiento STRING COMMENT 'Fecha de nacimiento del cliente',
# MAGIC   genero STRING COMMENT 'Género del cliente',
# MAGIC   ciudad STRING COMMENT 'Ciudad donde vive el cliente',
# MAGIC   total_ventas INTEGER COMMENT 'Total de ventas realizadas al cliente',
# MAGIC   total_productos INTEGER COMMENT 'Total productos únicos comprados por el cliente',
# MAGIC   cantidad_productos_comprados INTEGER COMMENT 'Cantidad de productos comprados por el cliente',
# MAGIC   total_monto DOUBLE COMMENT 'Monto pagado por el cliente',
# MAGIC   last_venta_id STRING COMMENT 'Última venta realizada al cliente',
# MAGIC   last_producto_id STRING COMMENT 'Último producto adquirido por el cliente',
# MAGIC   last_cantidad INTEGER COMMENT 'Cantidad de productos comprados por el cliente en la última venta',
# MAGIC   last_monto_total DOUBLE COMMENT 'Monto pagado por el cliente en la última venta',
# MAGIC   last_canal STRING COMMENT 'Último canal utilizado por el cliente',
# MAGIC   inserted_at TIMESTAMP COMMENT 'Timestamp cuando el registro fue insertado'
# MAGIC )
# MAGIC COMMENT 'Vista materializada que contiene el perfil del cliente'
# MAGIC AS
# MAGIC WITH rank_venta AS (
# MAGIC   SELECT
# MAGIC     cod_mes,
# MAGIC     venta_id,
# MAGIC     cliente_id,
# MAGIC     producto_id,
# MAGIC     fecha_venta,
# MAGIC     cantidad,
# MAGIC     monto_total,
# MAGIC     canal,
# MAGIC     -- rank() OVER(PARTITION BY cliente_id ORDER BY fecha_venta DESC, canal ASC, venta_id ASC) AS rnk,
# MAGIC     rank() OVER(
# MAGIC       PARTITION BY cliente_id 
# MAGIC       ORDER BY fecha_venta DESC, 
# MAGIC       CASE
# MAGIC         WHEN canal = 'tienda' THEN 1 
# MAGIC         WHEN canal = 'web' THEN 2 
# MAGIC         WHEN canal = 'app' THEN 3 
# MAGIC         ELSE 4
# MAGIC       END ASC,
# MAGIC       venta_id ASC
# MAGIC       ) AS rnk
# MAGIC   FROM g0_cmc_ventas.gold.vw_ventas
# MAGIC ),
# MAGIC agg_venta(
# MAGIC   SELECT
# MAGIC     cliente_id,
# MAGIC     CAST(COUNT(DISTINCT venta_id) AS INTEGER) AS total_ventas,
# MAGIC     CAST(COUNT(*) AS INTEGER) AS total_productos,
# MAGIC     CAST(SUM(cantidad) AS INTEGER) AS cantidad_productos_comprados,
# MAGIC     CAST(SUM(monto_total) AS DOUBLE) AS total_monto
# MAGIC   FROM rank_venta
# MAGIC   GROUP BY
# MAGIC     cliente_id
# MAGIC )
# MAGIC SELECT
# MAGIC   cli.cliente_id,
# MAGIC   cli.nombre,
# MAGIC   cli.email,
# MAGIC   g0_catalog.default.encrypt_col(cli.fecha_nacimiento) AS fecha_nacimiento,
# MAGIC   cli.genero,
# MAGIC   cli.ciudad,
# MAGIC   agg.total_ventas,
# MAGIC   agg.total_productos,
# MAGIC   agg.cantidad_productos_comprados,
# MAGIC   agg.total_monto,
# MAGIC   vta.venta_id AS last_venta_id,
# MAGIC   vta.producto_id AS last_producto_id,
# MAGIC   vta.cantidad AS last_cantidad,
# MAGIC   vta.monto_total AS last_monto_total,
# MAGIC   vta.canal AS last_canal,
# MAGIC   current_timestamp() AS inserted_at
# MAGIC FROM g0_mkt_clientes.gold.vw_clientes cli
# MAGIC LEFT JOIN agg_venta agg ON cli.cliente_id = agg.cliente_id
# MAGIC LEFT JOIN rank_venta vta ON cli.cliente_id = vta.cliente_id AND vta.rnk = 1

# COMMAND ----------

# MAGIC %sql
# MAGIC ALTER TABLE g0_mkt_clientes.silver.mv_clientes_perfil
# MAGIC ALTER COLUMN email SET TAGS ('PII');
# MAGIC
# MAGIC ALTER TABLE g0_mkt_clientes.silver.mv_clientes_perfil
# MAGIC ALTER COLUMN fecha_nacimiento SET TAGS ('PII');
# MAGIC
# MAGIC ALTER TABLE g0_mkt_clientes.silver.mv_clientes_perfil
# MAGIC ALTER COLUMN genero SET TAGS ('sensible');

# COMMAND ----------

# MAGIC %sql
# MAGIC -- GRANT REFRESH ON TABLE g0_mkt_clientes.silver.mv_clientes_perfil TO `utec-de`;

# COMMAND ----------

# MAGIC %sql
# MAGIC REFRESH MATERIALIZED VIEW g0_mkt_clientes.silver.mv_clientes_perfil