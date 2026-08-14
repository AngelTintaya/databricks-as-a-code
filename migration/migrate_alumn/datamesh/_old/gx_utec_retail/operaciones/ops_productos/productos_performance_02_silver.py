# Databricks notebook source
from datetime import datetime
from dateutil.relativedelta import relativedelta

# COMMAND ----------

# dbutils.widgets.text('FECHA_ACTUAL', '2024-02-01')

# COMMAND ----------

FECHA_ACTUAL = dbutils.widgets.get("FECHA_ACTUAL")
FECHA_ACTUAL_DT = datetime.strptime(FECHA_ACTUAL, '%Y-%m-%d') or datetime.now()
CODMES = (FECHA_ACTUAL_DT - relativedelta(months=1)).strftime('%Y%m')

# COMMAND ----------

FECHA_ACTUAL

# COMMAND ----------

spark.sql(
  f"""
  CREATE OR REPLACE TEMPORARY VIEW inventario_mes AS
    SELECT
      i.cod_mes,
      i.producto_id,
      i.producto_nombre,
      i.stock
    FROM g0_ops_productos.gold.vw_inventario i
    WHERE i.cod_mes = {CODMES}
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
    FROM g0_cmc_ventas.gold.vw_ventas v
    WHERE v.cod_mes = {CODMES}
    GROUP BY
        v.cod_mes,
        v.producto_id
  """
)

# COMMAND ----------

# MAGIC %sql
# MAGIC INSERT INTO g0_ops_productos.silver.hm_producto_performance (
# MAGIC   periodo,
# MAGIC   producto_id,
# MAGIC   producto_nombre,
# MAGIC   total_ventas,
# MAGIC   stock_actual,
# MAGIC   rotacion,
# MAGIC   ranking_rotacion,
# MAGIC   inserted_at
# MAGIC )
# MAGIC WITH ventas_inventario AS (
# MAGIC   SELECT
# MAGIC     i.cod_mes,
# MAGIC     i.producto_id,
# MAGIC     i.producto_nombre,
# MAGIC     COALESCE(v.total_ventas, 0) AS total_ventas,
# MAGIC     i.stock AS stock_actual,
# MAGIC     ROUND(CASE WHEN i.stock > 0 THEN v.total_ventas / i.stock ELSE NULL END, 2) AS rotacion
# MAGIC   FROM inventario_mes i
# MAGIC   LEFT JOIN ventas_mes v ON i.cod_mes = v.cod_mes AND i.producto_id = v.producto_id
# MAGIC )
# MAGIC SELECT
# MAGIC   cod_mes AS periodo,
# MAGIC   producto_id,
# MAGIC   producto_nombre,
# MAGIC   total_ventas,
# MAGIC   stock_actual,
# MAGIC   rotacion,
# MAGIC   RANK() OVER (ORDER BY rotacion DESC) AS ranking_rotacion,
# MAGIC   current_timestamp() AS inserted_at
# MAGIC FROM ventas_inventario;

# COMMAND ----------

# MAGIC %sql
# MAGIC OPTIMIZE g0_ops_productos.silver.hm_producto_performance

# COMMAND ----------

# MAGIC %sql
# MAGIC -- DESCRIBE HISTORY g0_ops_productos.silver.hm_producto_performance

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS g0_ops_productos.silver.um_producto_performance

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE g0_ops_productos.silver.um_producto_performance
# MAGIC AS
# MAGIC SELECT
# MAGIC   periodo,
# MAGIC   producto_id,
# MAGIC   producto_nombre,
# MAGIC   total_ventas,
# MAGIC   stock_actual,
# MAGIC   rotacion,
# MAGIC   ranking_rotacion,
# MAGIC   inserted_at
# MAGIC FROM g0_ops_productos.silver.hm_producto_performance
# MAGIC WHERE periodo = (SELECT periodo FROM g0_ops_productos.silver.hm_producto_performance ORDER BY periodo DESC LIMIT 1)
# MAGIC ;