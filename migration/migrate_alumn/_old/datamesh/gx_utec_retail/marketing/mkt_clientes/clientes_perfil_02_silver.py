# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook will NOT run in Pipeline
# MAGIC - Views and Materialized Views only needs to be created the first time
# MAGIC - Materialized views only will beed to be REFRESHED (Point to DataPlatform's REFRESH notebook)

# COMMAND ----------

# MAGIC %md
# MAGIC ## CHOOSE SERVERLESS COMPUTE

# COMMAND ----------

# MAGIC %run ./__clientes_parameter

# COMMAND ----------

# MAGIC %md
# MAGIC ### Dataproduct Parameters
# MAGIC - **IMPORTANT!!!**: SILVER_TB_CLIENTES is being used instead of GOLD_VW_CLIENTES bc need to write encrypted data

# COMMAND ----------

dict_tables = get_medallion_tables()
SILVER_MV_CLIENTES_PERFIL = dict_tables.get('SILVER_MV_CLIENTES_PERFIL')
GOLD_VW_VENTAS = dict_tables.get('GOLD_VW_VENTAS')
SILVER_TB_CLIENTES = dict_tables.get('SILVER_TB_CLIENTES')
# GOLD_VW_CLIENTES = dict_tables.get('GOLD_VW_CLIENTES')

# COMMAND ----------

print('SILVER_MV_CLIENTES_PERFIL\t:', SILVER_MV_CLIENTES_PERFIL)
print('GOLD_VW_VENTAS\t\t\t:', GOLD_VW_VENTAS)
print('SILVER_TB_CLIENTES\t\t:', SILVER_TB_CLIENTES)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Widget Parameters
# MAGIC - Parameters should be set as a widget to be able to be read in WAREHOUSE
# MAGIC - Do NOT delete the widget until Materialied View is created

# COMMAND ----------

dbutils.widgets.text('SILVER_MV_CLIENTES_PERFIL', SILVER_MV_CLIENTES_PERFIL)
dbutils.widgets.text('GOLD_VW_VENTAS', GOLD_VW_VENTAS)
dbutils.widgets.text('SILVER_TB_CLIENTES', SILVER_TB_CLIENTES)

# COMMAND ----------

print('SILVER_MV_CLIENTES_PERFIL\t:', dbutils.widgets.get("SILVER_MV_CLIENTES_PERFIL"))
print('GOLD_VW_VENTAS\t\t\t:', dbutils.widgets.get("GOLD_VW_VENTAS"))
print('SILVER_TB_CLIENTES\t\t:', dbutils.widgets.get("SILVER_TB_CLIENTES"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## CHOOSE WAREHOUSE COMPUTE
# MAGIC - Materialized Views only run in Warehouse Compute
# MAGIC - All Materialized Views should store only encrypted values if exists

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP MATERIALIZED VIEW IF EXISTS ${SILVER_MV_CLIENTES_PERFIL}

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE MATERIALIZED VIEW ${SILVER_MV_CLIENTES_PERFIL}
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
# MAGIC   FROM ${GOLD_VW_VENTAS}
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
# MAGIC   cli.fecha_nacimiento,
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
# MAGIC FROM ${SILVER_TB_CLIENTES} cli
# MAGIC LEFT JOIN agg_venta agg ON cli.cliente_id = agg.cliente_id
# MAGIC LEFT JOIN rank_venta vta ON cli.cliente_id = vta.cliente_id AND vta.rnk = 1

# COMMAND ----------

# MAGIC %sql
# MAGIC ALTER TABLE ${SILVER_MV_CLIENTES_PERFIL}
# MAGIC ALTER COLUMN email SET TAGS ('PII');
# MAGIC
# MAGIC ALTER TABLE ${SILVER_MV_CLIENTES_PERFIL}
# MAGIC ALTER COLUMN fecha_nacimiento SET TAGS ('PII');
# MAGIC
# MAGIC ALTER TABLE ${SILVER_MV_CLIENTES_PERFIL}
# MAGIC ALTER COLUMN genero SET TAGS ('sensible');

# COMMAND ----------

# MAGIC %sql
# MAGIC -- GRANT REFRESH ON TABLE ${SILVER_MV_CLIENTES_PERFIL} TO `utec-de`;

# COMMAND ----------

# MAGIC %sql
# MAGIC REFRESH MATERIALIZED VIEW ${SILVER_MV_CLIENTES_PERFIL}