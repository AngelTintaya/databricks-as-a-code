# Databricks notebook source
my_catalog = 'g3_pag_saldos'

# COMMAND ----------

# spark.sql(f"""DROP VIEW IF EXISTS {my_catalog}.gold.vw_pagos_por_orden""")
spark.sql(f"""DROP VIEW IF EXISTS {my_catalog}.gold.vw_ordenes_sin_pagar""")

# COMMAND ----------

# spark.sql(
#     f"""
#     CREATE OR REPLACE VIEW {my_catalog}.gold.vw_pagos_por_orden AS 
#     SELECT
#         ejer_id,
#         orden_id,
#         sum(pago_monto) AS pago_total
#     FROM {my_catalog}.silver.tb_pagos
#     GROUP BY ejer_id, orden_id
#     ORDER BY ejer_id, orden_id
#     """
# )

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {my_catalog}.gold.vw_ordenes_sin_pagar
    COMMENT "Generación de la vista con el consolidado de las órdenes de servicio pendientes de pago."
    AS
    WITH tmp_pagos_por_orden AS (
        SELECT
            ejer_id,
            orden_id,
            sum(pago_monto) AS pago_total
        FROM {my_catalog}.silver.tb_pagos
        GROUP BY ejer_id, orden_id
    )
    SELECT
        a.ejer_id,
        a.orden_id,
        a.orden_fecha,
        a.locador_id,
        c.locador_nombre,
        a.orden_total,
        COALESCE(b.pago_total, 0) AS pago_total,
        a.orden_total - COALESCE(b.pago_total, 0) AS saldo_total
    FROM {my_catalog}.silver.tb_ordenes a
    LEFT JOIN tmp_pagos_por_orden b
    ON a.ejer_id = b.ejer_id AND a.orden_id = b.orden_id
    LEFT JOIN {my_catalog}.silver.tb_locadores c
    ON a.ejer_id = c.ejer_id AND a.locador_id = c.locador_id
    WHERE a.orden_total - COALESCE(b.pago_total, 0) <> 0 and c.locador_nombre IS NOT NULL
    ORDER BY a.ejer_id, a.orden_id
    """
)

# COMMAND ----------

# spark.sql(f"""SELECT * FROM {my_catalog}.gold.vw_pagos_por_orden""").display()

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.gold.vw_ordenes_sin_pagar""").display()