# Databricks notebook source
# MAGIC %run ./__clientes_parameter

# COMMAND ----------

dict_support_tables = get_support_tables()
SUPPORT_TB_ERRORES_VALIDACION = dict_support_tables.get('SUPPORT_TB_ERRORES_VALIDACION')
SUPPORT_TB_CUARENTENA_RAW_CLIENTES = dict_support_tables.get('SUPPORT_TB_CUARENTENA_RAW_CLIENTES')

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {SUPPORT_TB_ERRORES_VALIDACION}')

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {SUPPORT_TB_CUARENTENA_RAW_CLIENTES}')

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {SUPPORT_TB_ERRORES_VALIDACION}
    (
        valid_id BIGINT GENERATED ALWAYS AS IDENTITY,
        process STRING,
        total_errores BIGINT,
        tipo_error STRING,
        created_at DATE
    )
    """
    )

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {SUPPORT_TB_CUARENTENA_RAW_CLIENTES}
    (
        cliente_id STRING,
        nombre STRING,
        email STRING,
        fecha_nacimiento STRING,
        genero STRING,
        ubicacion STRING,
        fecha STRING,
        inserted_at TIMESTAMP
    )
    """
    )