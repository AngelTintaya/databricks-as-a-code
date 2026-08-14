# Databricks notebook source
my_catalog = 'g3_eva_servicios'

# COMMAND ----------

spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.silver.tb_catalogo_servicios""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.silver.tb_ordenes_det""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.silver.tb_sedes""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.silver.tb_metas""")

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {my_catalog}.silver.tb_catalogo_servicios
    COMMENT "Regularización de los campos de la tabla catálogo de servicios."
    AS 
    SELECT
        2020 AS ejer_id,
        _c0 AS adquis_tipo,
        CAST(_c1 AS STRING) AS servicio_id,
        _c2 AS servicio_id_alterno,
        _c3 AS servicio_descripcion,
        TRUE as servicio_estado,
        inserted_at
   FROM {my_catalog}.bronze.tb_catalogo_servicios
   WHERE _c4 = "A"
    """
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {my_catalog}.silver.tb_ordenes_det
    COMMENT "Regularización de los campos de la tabla detalles de las órdenes de servicio."
    AS 
    SELECT
        _c0 AS ejer_id,
        _c1 AS adquis_tipo,
        _c2 AS orden_id,
        CAST(_c3 AS STRING) AS servicio_id,
        CAST(_c5 AS DECIMAL(7,2)) AS orden_cantidad,
        CAST(_c4 AS DECIMAL(7,2)) AS orden_prec_unit,
        CAST(_c6 AS DECIMAL(10,2)) AS orden_subtotal,
        _c7 AS orden_especificaciones,
        TRUE as orden_estado,
        inserted_at
    FROM {my_catalog}.bronze.tb_ordenes_det
    """
)

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.silver.tb_catalogo_servicios""").display()

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.silver.tb_ordenes_det""").display()