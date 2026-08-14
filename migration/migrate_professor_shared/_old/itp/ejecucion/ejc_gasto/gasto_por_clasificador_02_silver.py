# Databricks notebook source
my_catalog = 'g3_ejc_gasto'

# COMMAND ----------

spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.silver.tb_ordenes""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.silver.tb_pedidos""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.silver.tb_pedidos_det""")

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {my_catalog}.silver.tb_ordenes
    COMMENT "Regularización de los campos de la tabla órdenes de servicio."
    AS 
    SELECT
        _c0 AS ejer_id,
        _c1 AS adquis_tipo,
        _c2 AS orden_id,
        _c3 AS orden_fecha,
        _c4 AS locador_id,
        _c5 AS pedido_id,
        _c6 AS orden_concepto,
        _c7 AS tasa_impos,
        _c8 AS moneda_id,
        CAST(_c9 AS DECIMAL(10,2)) AS orden_total,
        TRUE as orden_estado,
        inserted_at
   FROM {my_catalog}.bronze.tb_ordenes
   WHERE _c9 > 0
    """
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {my_catalog}.silver.tb_pedidos
    COMMENT "Regularización de los campos de la tabla pedidos de servicio."
    AS 
    SELECT
        _c0 AS ejer_id,
        _c1 AS adquis_tipo,
        _c2 AS pedido_id,
        _c3 AS pedido_fecha,
        _c4 AS sede_id,
        _c5 AS meta_id,
        _c6 AS tarea_id,
        _c7 AS pedido_motivo,
        _c8 AS moneda_id,
        TRUE as pedido_estado,
        inserted_at
   FROM {my_catalog}.bronze.tb_pedidos
    """
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {my_catalog}.silver.tb_pedidos_det
    COMMENT "Regularización de los campos de la tabla detalles de los pedidos de servicio."
    AS 
    SELECT
        _c0 AS ejer_id,
        _c1 AS adquis_tipo,
        _c2 AS pedido_id,
        _c3 AS servicio_id,
        CAST(_c4 AS DECIMAL(7,2)) AS pedido_cant_soli,
        CAST(_c5 AS DECIMAL(7,2)) AS pedido_cant_apro,
        CAST(_c6 AS DECIMAL(7,2)) AS pedido_prec_unit,
        CAST(_c7 AS DECIMAL(10,2)) AS pedido_subtotal,
        _c8 AS clasificador_id,
        TRUE as pedido_estado,
        inserted_at
    FROM {my_catalog}.bronze.tb_pedidos_det
    WHERE _c7 > 0
    """
)

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.silver.tb_ordenes""").display()

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.silver.tb_pedidos""").display()

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.silver.tb_pedidos_det""").display()