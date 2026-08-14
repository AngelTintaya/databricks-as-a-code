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
SILVER_TB_CLIENTES = dict_tables.get('SILVER_TB_CLIENTES')
GOLD_VW_CLIENTES = dict_tables.get('GOLD_VW_CLIENTES')

# COMMAND ----------

print('SILVER_TB_CLIENTES\t:', SILVER_TB_CLIENTES)
print('GOLD_VW_CLIENTES\t:', GOLD_VW_CLIENTES)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Process

# COMMAND ----------

spark.sql(f'DROP VIEW IF EXISTS {GOLD_VW_CLIENTES}')

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {GOLD_VW_CLIENTES}
    (
        cliente_id,
        nombre,
        email COMMENT 'Email del cliente',
        fecha_nacimiento COMMENT 'Fecha de nacimiento del cliente',
        genero COMMENT 'Género del cliente',
        ciudad,
        created_at,
        inserted_at
    )
    COMMENT 'Vista que contiene información curada de clientes'
    AS
    SELECT
        cliente_id,
        nombre,
        g0_catalog.default.pii_mask(email) AS email,
        g0_catalog.default.pii_col(fecha_nacimiento) AS fecha_nacimiento,
        g0_catalog.default.pii_mask(genero) AS genero,
        ciudad,
        created_at,
        inserted_at
    FROM {SILVER_TB_CLIENTES}
    """
    )