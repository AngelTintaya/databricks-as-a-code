# Databricks notebook source
my_catalog = 'g3_pag_saldos'

# COMMAND ----------

spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.silver.tb_ordenes""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.silver.tb_pedidos""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.silver.tb_pagos""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.silver.tb_locadores""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.silver.tb_sedes""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.silver.tb_metas""")

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
        CAST(_c3 AS DATE) AS orden_fecha,
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
        CAST(_c3 AS DATE) AS pedido_fecha,
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
    CREATE OR REPLACE TABLE {my_catalog}.silver.tb_pagos
    COMMENT "Regularización de los campos de la tabla pagos de órdenes."
    AS 
    SELECT
        _c0 AS ejer_id,
        _c1 AS adquis_tipo,
        _c2 AS locador_id,
        _c3 AS orden_id,
        CAST(_c4 AS DATE) AS pago_fecha,
        CAST(_c5 AS DECIMAL(10,2)) AS pago_monto,
        TRUE as pago_estado,
        inserted_at
   FROM {my_catalog}.bronze.tb_pagos
    """
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {my_catalog}.silver.tb_locadores
    COMMENT "Regularización de los campos de la tabla locadores de servicios."
    AS 
    SELECT
        2020 AS ejer_id,
        _c1 AS locador_id,
        _c0 AS locador_ruc,
        _c2 AS locador_nombre,
        _c3 AS locador_giro,
        _c4 AS locador_direccion,
        TRUE as locador_estado,
        inserted_at
    FROM {my_catalog}.bronze.tb_locadores
    --WHERE _c8 = "P"
    """
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {my_catalog}.silver.tb_sedes
    COMMENT "Regularización de los campos de la tabla sedes de la entidad."
    AS 
    SELECT
        _c0 AS ejer_id,
        _c1 AS sede_id,
        _c2 AS sede_nombre,
        _c3 AS sede_nombre_corto,
        TRUE AS sede_estado,
        inserted_at
   FROM {my_catalog}.bronze.tb_sedes
   WHERE _c4 = "A"
    """
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {my_catalog}.silver.tb_metas
    COMMENT "Regularización de los campos de la tabla metas de gestión."
    AS 
    SELECT
        _c0 AS ejer_id,
        _c1 AS meta_id,
        _c3 AS meta_nombre,
        TRUE AS meta_estado,
        inserted_at
   FROM {my_catalog}.bronze.tb_metas
   WHERE _c4 = "A"
    """
)

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.silver.tb_ordenes""").display()

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.silver.tb_pedidos""").display()

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.silver.tb_pagos""").display()

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.silver.tb_locadores""").display()

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.silver.tb_sedes""").display()

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.silver.tb_metas""").display()