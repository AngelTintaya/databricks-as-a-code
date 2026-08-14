# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook will NOT run in Pipeline
# MAGIC - Views and Materialized Views only needs to be created the first time
# MAGIC - Materialized views only will beed to be REFRESHED (Point to DataPlatform's REFRESH notebook)

# COMMAND ----------

# MAGIC %md
# MAGIC ## CHOOSE SERVERLESS COMPUTE

# COMMAND ----------

dbutils.widgets.text('SILVER_MV_INVENTARIO', 'gx_ops_productos.silver.mv_inventario')
dbutils.widgets.text('BRONZE_TB_RAW_INVENTARIO', 'gx_ops_productos.bronze.raw_inventario')

# COMMAND ----------

print('SILVER_MV_INVENTARIO\t\t:', dbutils.widgets.get("SILVER_MV_INVENTARIO"))
print('BRONZE_TB_RAW_INVENTARIO\t: ',dbutils.widgets.get("BRONZE_TB_RAW_INVENTARIO"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## CHOOSE WAREHOUSE COMPUTE
# MAGIC Materialized Views only run in Warehouse Compute

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP MATERIALIZED VIEW IF EXISTS ${SILVER_MV_INVENTARIO}

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE MATERIALIZED VIEW ${SILVER_MV_INVENTARIO}
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
# MAGIC   FROM ${BRONZE_TB_RAW_INVENTARIO}
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
# MAGIC REFRESH MATERIALIZED VIEW ${SILVER_MV_INVENTARIO}