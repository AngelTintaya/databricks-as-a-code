# Databricks notebook source
my_catalog = 'g3_eva_servicios'

# COMMAND ----------

spark.sql(f"""DROP VIEW IF EXISTS {my_catalog}.gold.vw_evaluacion_por_servicio""")
spark.sql(f"""DROP VIEW IF EXISTS {my_catalog}.gold.vw_sedes""")
spark.sql(f"""DROP VIEW IF EXISTS {my_catalog}.gold.vw_metas""")

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {my_catalog}.gold.vw_evaluacion_por_servicio
    COMMENT "Generación de la vista con el consolidado de la evaluación del gasto por servicio."
    AS 
    SELECT
        a.ejer_id,
        a.servicio_id,
        b.servicio_descripcion,
        sum(a.orden_subtotal) as servicio_total
    FROM {my_catalog}.silver.tb_ordenes_det a
    LEFT JOIN {my_catalog}.silver.tb_catalogo_servicios b
    ON a.ejer_id = b.ejer_id AND a.servicio_id = b.servicio_id
    WHERE a.orden_estado = TRUE and b.servicio_estado = TRUE
    GROUP BY a.ejer_id, a.servicio_id, b.servicio_descripcion
    ORDER BY servicio_total DESC
    """
)

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.gold.vw_evaluacion_por_servicio""").display()