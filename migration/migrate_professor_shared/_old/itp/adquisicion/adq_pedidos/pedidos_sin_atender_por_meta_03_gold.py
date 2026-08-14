# Databricks notebook source
from pyspark.sql.functions import current_date

# COMMAND ----------

my_catalog = 'g3_adq_pedidos'

# COMMAND ----------

spark.sql(f"""DROP VIEW IF EXISTS {my_catalog}.gold.vw_pedidos_sin_atender_por_meta""")

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {my_catalog}.gold.vw_pedidos_sin_atender_por_meta
    COMMENT "Generación de la vista con el consolidado de los pedidos de servicio pendientes de atender por meta."
    AS 
    SELECT
        a.ejer_id,
        a.meta_id,
        c.meta_nombre,
        a.pedido_id,
        a.pedido_fecha,
        datediff(current_date(), a.pedido_fecha) as pedido_demora,
        a.pedido_motivo
    FROM {my_catalog}.silver.tb_pedidos a
    LEFT JOIN {my_catalog}.silver.tb_ordenes b
    ON a.ejer_id = b.ejer_id AND a.pedido_id = b.pedido_id
    LEFT JOIN {my_catalog}.silver.tb_metas c
    ON a.ejer_id = c.ejer_id AND a.meta_id = c.meta_id
    WHERE b.pedido_id IS NULL
    ORDER BY a.ejer_id, a.meta_id, c.meta_nombre, a.pedido_id
    """
)

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.gold.vw_pedidos_sin_atender_por_meta""").display()