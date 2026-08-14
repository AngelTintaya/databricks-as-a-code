# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook will NOT run in Pipeline
# MAGIC - Views only needs to be created the first time

# COMMAND ----------

# MAGIC %run ./__clientes_parameter

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dataproduct Parameters

# COMMAND ----------

dict_tables = get_medallion_tables()
SILVER_MV_CLIENTES_PERFIL = dict_tables.get('SILVER_MV_CLIENTES_PERFIL')
GOLD_VW_CLIENTES_PERFIL = dict_tables.get('GOLD_VW_CLIENTES_PERFIL')

# COMMAND ----------

print('SILVER_MV_CLIENTES_PERFIL\t:', SILVER_MV_CLIENTES_PERFIL)
print('GOLD_VW_CLIENTES_PERFIL\t\t:', GOLD_VW_CLIENTES_PERFIL)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Process

# COMMAND ----------

spark.sql(f'DROP VIEW IF EXISTS {GOLD_VW_CLIENTES_PERFIL}')

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {GOLD_VW_CLIENTES_PERFIL}
    (
        cliente_id,
        nombre,
        email COMMENT 'Email del cliente',
        fecha_nacimiento COMMENT 'Fecha de nacimiento del cliente',
        genero COMMENT 'Género del cliente',
        ciudad,
        total_ventas,
        total_productos,
        cantidad_productos_comprados,
        total_monto,
        last_venta_id,
        last_producto_id,
        last_cantidad,
        last_monto_total,
        last_canal,
        inserted_at
    )
    COMMENT 'Vista que contiene el perfil del cliente'
    AS
    SELECT
        cliente_id,
        nombre,
        g0_catalog.default.pii_mask(email) AS email,
        g0_catalog.default.pii_col(fecha_nacimiento) AS fecha_nacimiento,
        g0_catalog.default.pii_mask(genero) AS genero,
        ciudad,
        total_ventas,
        total_productos,
        cantidad_productos_comprados,
        total_monto,
        last_venta_id,
        last_producto_id,
        last_cantidad,
        last_monto_total,
        last_canal,
        inserted_at
    FROM {SILVER_MV_CLIENTES_PERFIL}
    """
    )