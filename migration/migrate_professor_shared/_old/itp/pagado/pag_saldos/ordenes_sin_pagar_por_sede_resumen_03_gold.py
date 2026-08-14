# Databricks notebook source
my_catalog = 'g3_pag_saldos'

# COMMAND ----------

spark.sql(f"""DROP VIEW IF EXISTS {my_catalog}.gold.vw_ordenes_sin_pagar_por_sede_resumen""")

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {my_catalog}.gold.vw_ordenes_sin_pagar_por_sede_resumen
    COMMENT "Generación de la vista con el consolidado resumido de las órdenes de servicio pendientes de pago por sede."
    AS
    SELECT
        ejer_id,
        sede_id,
        sede_nombre,
        sum(saldo_total) AS saldo_total_sede
    FROM {my_catalog}.gold.vw_ordenes_sin_pagar_por_sede
    GROUP BY ejer_id, sede_id, sede_nombre
    ORDER BY ejer_id, sede_id, sede_nombre
    """
)

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.gold.vw_ordenes_sin_pagar_por_sede_resumen""").display()