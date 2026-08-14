# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook will NOT run in Pipeline
# MAGIC - Views only needs to be created the first time

# COMMAND ----------

dbutils.widgets.text('SILVER_MV_INVENTARIO', 'g0_ops_productos.silver.mv_inventario')
dbutils.widgets.text('GOLD_VW_INVENTARIO', 'g0_ops_productos.gold.vw_inventario')

# COMMAND ----------

SILVER_MV_INVENTARIO = dbutils.widgets.get("SILVER_MV_INVENTARIO")
GOLD_VW_INVENTARIO = dbutils.widgets.get("GOLD_VW_INVENTARIO")

# COMMAND ----------

print('SILVER_MV_INVENTARIO\t:', SILVER_MV_INVENTARIO)
print('GOLD_VW_INVENTARIO\t:', GOLD_VW_INVENTARIO)

# COMMAND ----------

spark.sql(f'DROP VIEW IF EXISTS {GOLD_VW_INVENTARIO}')

# COMMAND ----------

spark.sql(f"""
          CREATE OR REPLACE VIEW {GOLD_VW_INVENTARIO}
          COMMENT 'Vista que contiene información del inventario'
          AS
          SELECT
            cod_mes,
            producto_id,
            producto_nombre,
            stock,
            sede,
            created_at,
            inserted_at
          FROM {SILVER_MV_INVENTARIO}
          """)