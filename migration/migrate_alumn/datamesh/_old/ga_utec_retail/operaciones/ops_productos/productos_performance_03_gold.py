# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook will NOT run in Pipeline
# MAGIC - Views only needs to be created the first time

# COMMAND ----------

dbutils.widgets.text('SILVER_TB_UM_PROD_PERF', 'ga_ops_productos.silver.um_producto_performance')
dbutils.widgets.text('SILVER_TB_HM_PROD_PERF', 'ga_ops_productos.silver.hm_producto_performance')
dbutils.widgets.text('GOLD_VW_UM_PROD_PERF', 'ga_ops_productos.gold.vw_um_producto_performance')
dbutils.widgets.text('GOLD_VW_HM_PROD_PERF', 'ga_ops_productos.gold.vw_hm_producto_performance')

# COMMAND ----------

SILVER_TB_UM_PROD_PERF = dbutils.widgets.get("SILVER_TB_UM_PROD_PERF")
SILVER_TB_HM_PROD_PERF = dbutils.widgets.get("SILVER_TB_HM_PROD_PERF")
GOLD_VW_UM_PROD_PERF = dbutils.widgets.get("GOLD_VW_UM_PROD_PERF")
GOLD_VW_HM_PROD_PERF = dbutils.widgets.get("GOLD_VW_HM_PROD_PERF")

# COMMAND ----------

print('SILVER_TB_UM_PROD_PERF\t:', SILVER_TB_UM_PROD_PERF)
print('SILVER_TB_HM_PROD_PERF\t:', SILVER_TB_HM_PROD_PERF)
print('GOLD_VW_UM_PROD_PERF\t:', GOLD_VW_UM_PROD_PERF)
print('GOLD_VW_HM_PROD_PERF\t:', GOLD_VW_HM_PROD_PERF)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {GOLD_VW_HM_PROD_PERF}
    COMMENT 'Vista histórica mensual que contiene el performance de cada producto'
    AS
    SELECT
        periodo,
        producto_id,
        producto_nombre,
        total_ventas,
        stock_actual,
        rotacion,
        ranking_rotacion,
        inserted_at
    FROM {SILVER_TB_HM_PROD_PERF}
    """
    )

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {GOLD_VW_UM_PROD_PERF}
    (
        periodo COMMENT 'Periodo de tiempo mensual en el que se calculó el performance',
        producto_id COMMENT 'Identificador único del producto',
        producto_nombre COMMENT 'Nombre del producto',
        total_ventas COMMENT 'Total de unidades vendidas en el periodo',
        stock_actual COMMENT 'Stock actual al cierre del periodo',
        rotacion COMMENT 'Ratio de rotación del producto en el periodo calculado como total_ventas / stock_actual.',
        ranking_rotacion COMMENT 'Ranking dentro del mes por rotación, orden descendente.',
        inserted_at COMMENT 'Timestamp en que se insertó este snapshot'
    )
    COMMENT 'Vista del último mes que contiene el performance de cada producto'
    AS
    SELECT
        periodo,
        producto_id,
        producto_nombre,
        total_ventas,
        stock_actual,
        rotacion,
        ranking_rotacion,
        inserted_at
    FROM {SILVER_TB_UM_PROD_PERF}
    """
    )