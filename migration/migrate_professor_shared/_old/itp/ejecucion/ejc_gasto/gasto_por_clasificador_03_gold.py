# Databricks notebook source
my_catalog = 'g3_ejc_gasto'

# COMMAND ----------

spark.sql(f"""DROP VIEW IF EXISTS {my_catalog}.gold.vw_gasto_por_clasificador""")

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {my_catalog}.gold.vw_gasto_por_clasificador
    COMMENT "Generación de la vista con el consolidado del gasto presupuestal por clasificador."
    AS 
    SELECT
        a.ejer_id,
        b.clasificador_id,
        sum(a.orden_total) as clasificador_total
    FROM {my_catalog}.silver.tb_ordenes a
    LEFT JOIN {my_catalog}.silver.tb_pedidos_det b
    ON a.ejer_id = b.ejer_id AND a.pedido_id = b.pedido_id
    WHERE a.orden_estado = TRUE and b.pedido_estado = TRUE
    GROUP BY a.ejer_id, b.clasificador_id
    ORDER BY clasificador_total DESC
    """
)

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.gold.vw_gasto_por_clasificador""").display()