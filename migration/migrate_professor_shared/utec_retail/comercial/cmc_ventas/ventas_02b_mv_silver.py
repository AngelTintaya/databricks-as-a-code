# Databricks notebook source
# MAGIC %md
# MAGIC # Cluster Compute

# COMMAND ----------

my_catalog = 'gx00_cmc_ventas'

# COMMAND ----------

dbutils.widgets.text('SILVER_VW_VENTAS', f'{my_catalog}.silver.vw_ventas')
dbutils.widgets.text('SILVER_MV_VENTAS', f'{my_catalog}.silver.mv_ventas')

# COMMAND ----------

# MAGIC %md
# MAGIC # SQL Warehouse Compute

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP MATERIALIZED VIEW IF EXISTS IDENTIFIER(:SILVER_MV_VENTAS)

# COMMAND ----------

# DBTITLE 1,Celda 6
# MAGIC %sql
# MAGIC CREATE OR REPLACE MATERIALIZED VIEW ${SILVER_MV_VENTAS}
# MAGIC (
# MAGIC   cod_mes STRING COMMENT 'Código del mes en que se realizó la venta en formato YYYYMM',
# MAGIC   venta_id STRING COMMENT 'Identificador único de la venta',
# MAGIC   cliente_id STRING COMMENT 'Identificador único del cliente',
# MAGIC   producto_id STRING COMMENT 'Identificador único del producto',
# MAGIC   fecha_venta DATE COMMENT 'Fecha en que se realizó la venta',
# MAGIC   cantidad INTEGER COMMENT 'Cantidad de productos vendidos',
# MAGIC   monto_total DOUBLE COMMENT 'Precio unitario por cada producto',
# MAGIC   canal STRING COMMENT 'Canal por el que se realizó la venta',
# MAGIC   created_at TIMESTAMP COMMENT 'Timestamp en que se creó el registro',
# MAGIC   inserted_at TIMESTAMP COMMENT 'Timestamp en que se actualizó el registro'
# MAGIC )
# MAGIC COMMENT 'Vista materializada que contiene el consolidado de ventas'
# MAGIC AS
# MAGIC SELECT
# MAGIC   DATE_FORMAT(fecha_venta, 'yyyyMM') AS cod_mes,
# MAGIC   venta_id,
# MAGIC   cliente_id,
# MAGIC   producto_id,
# MAGIC   fecha_venta,
# MAGIC   cantidad,
# MAGIC   monto_total,
# MAGIC   canal,
# MAGIC   CAST(fecha AS TIMESTAMP) as created_at,
# MAGIC   CURRENT_TIMESTAMP() AS inserted_at
# MAGIC FROM ${SILVER_VW_VENTAS}

# COMMAND ----------

# MAGIC %sql
# MAGIC REFRESH MATERIALIZED VIEW IDENTIFIER(:SILVER_MV_VENTAS)