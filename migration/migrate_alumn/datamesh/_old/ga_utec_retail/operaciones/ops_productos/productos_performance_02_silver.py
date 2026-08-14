# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook **WILL RUN** in Pipeline
# MAGIC - Need to create temporary views and insert into SILVER_TB_HM_PROD_PERF silver table
# MAGIC - Need to create SILVER_TB_UM_PROD_PERF silver table on top of SILVER_TB_HM_PROD_PERFsilver table.
# MAGIC - COMMENT widget creation: dbutils.widgets.text() -> It will be created in the pipeline

# COMMAND ----------

from datetime import datetime
from dateutil.relativedelta import relativedelta

# COMMAND ----------

# dbutils.widgets.text('GOLD_VW_INVENTARIO', 'ga_ops_productos.gold.vw_inventario')
# dbutils.widgets.text('GOLD_VW_VENTAS', 'ga_cmc_ventas.gold.vw_ventas')
# dbutils.widgets.text('SILVER_TB_UM_PROD_PERF', 'ga_ops_productos.silver.um_producto_performance')
# dbutils.widgets.text('SILVER_TB_HM_PROD_PERF', 'ga_ops_productos.silver.hm_producto_performance')
# dbutils.widgets.text('FECHA_ACTUAL', '2024-02-01')

# COMMAND ----------

GOLD_VW_INVENTARIO = dbutils.widgets.get("GOLD_VW_INVENTARIO")
GOLD_VW_VENTAS = dbutils.widgets.get("GOLD_VW_VENTAS")
SILVER_TB_UM_PROD_PERF = dbutils.widgets.get("SILVER_TB_UM_PROD_PERF")
SILVER_TB_HM_PROD_PERF = dbutils.widgets.get("SILVER_TB_HM_PROD_PERF")
FECHA_ACTUAL = dbutils.widgets.get("FECHA_ACTUAL")

FECHA_ACTUAL_DT = datetime.strptime(FECHA_ACTUAL, '%Y-%m-%d') or datetime.now()
CODMES_ANTERIOR = (FECHA_ACTUAL_DT - relativedelta(months=1)).strftime('%Y%m')

# COMMAND ----------

print('GOLD_VW_INVENTARIO\t:', GOLD_VW_INVENTARIO)
print('GOLD_VW_VENTAS\t\t:', GOLD_VW_VENTAS)
print('SILVER_TB_UM_PROD_PERF\t:', SILVER_TB_UM_PROD_PERF)
print('SILVER_TB_HM_PROD_PERF\t:', SILVER_TB_HM_PROD_PERF)
print('FECHA_ACTUAL\t\t:', FECHA_ACTUAL)
print('CODMES_ANTERIOR\t\t:', CODMES_ANTERIOR)

# COMMAND ----------

spark.sql(
  f"""
  CREATE OR REPLACE TEMPORARY VIEW inventario_mes AS
    SELECT
      i.cod_mes,
      i.producto_id,
      i.producto_nombre,
      i.stock
    FROM {GOLD_VW_INVENTARIO} i
    WHERE i.cod_mes = {CODMES_ANTERIOR}
  """
)

# COMMAND ----------

spark.sql(
  f"""
  CREATE OR REPLACE TEMPORARY VIEW ventas_mes AS
    SELECT
        v.cod_mes,
        v.producto_id,
        SUM(v.cantidad) AS total_ventas
    FROM {GOLD_VW_VENTAS} v
    WHERE v.cod_mes = {CODMES_ANTERIOR}
    GROUP BY
        v.cod_mes,
        v.producto_id
  """
)

# COMMAND ----------

spark.sql(
    f"DELETE FROM {SILVER_TB_HM_PROD_PERF} WHERE periodo = {CODMES_ANTERIOR}"
)

# COMMAND ----------

spark.sql(
    f"""
    INSERT INTO {SILVER_TB_HM_PROD_PERF} (
    periodo,
    producto_id,
    producto_nombre,
    total_ventas,
    stock_actual,
    rotacion,
    ranking_rotacion,
    inserted_at
    )
    WITH ventas_inventario AS (
    SELECT
        i.cod_mes,
        i.producto_id,
        i.producto_nombre,
        COALESCE(v.total_ventas, 0) AS total_ventas,
        i.stock AS stock_actual,
        ROUND(CASE WHEN i.stock > 0 THEN v.total_ventas / i.stock ELSE NULL END, 2) AS rotacion
    FROM inventario_mes i
    LEFT JOIN ventas_mes v ON i.cod_mes = v.cod_mes AND i.producto_id = v.producto_id
    )
    SELECT
    cod_mes AS periodo,
    producto_id,
    producto_nombre,
    total_ventas,
    stock_actual,
    rotacion,
    RANK() OVER (ORDER BY rotacion DESC) AS ranking_rotacion,
    current_timestamp() AS inserted_at
    FROM ventas_inventario
    """
    )

# COMMAND ----------

spark.sql(f'OPTIMIZE {SILVER_TB_HM_PROD_PERF}')

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {SILVER_TB_UM_PROD_PERF}')

# COMMAND ----------

spark.sql(
    f"""
    CREATE TABLE {SILVER_TB_UM_PROD_PERF}
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
    WHERE periodo = (SELECT periodo FROM {SILVER_TB_HM_PROD_PERF} ORDER BY periodo DESC LIMIT 1)
    """
)