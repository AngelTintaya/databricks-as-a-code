# Databricks notebook source
# MAGIC %run ./__clientes_parameter

# COMMAND ----------

dict_tables = get_medallion_tables()
SILVER_TB_CLIENTES = dict_tables.get('SILVER_TB_CLIENTES')

# COMMAND ----------

SILVER_TB_CLIENTES

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {SILVER_TB_CLIENTES}')

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {SILVER_TB_CLIENTES}
    (
        cliente_id STRING COMMENT 'Identificador único del cliente',
        nombre STRING COMMENT 'Nombre del cliente',
        email STRING COMMENT 'Email del cliente',
        fecha_nacimiento STRING COMMENT 'Fecha de nacimiento del cliente',
        genero STRING COMMENT 'Género del cliente',
        ciudad STRING COMMENT 'Ciudad donde vive el cliente',
        created_at TIMESTAMP COMMENT 'Timestamp cuando el registro fue creado',
        inserted_at TIMESTAMP COMMENT 'Timestamp cuando el registro fue insertado'
    )
    COMMENT 'Contiene información curada del cliente'
    """
    )

# COMMAND ----------

spark.sql(
    f"""
    ALTER TABLE {SILVER_TB_CLIENTES}
    ALTER COLUMN email SET TAGS ("PII")
    """
    )

# COMMAND ----------

spark.sql(
    f"""
    ALTER TABLE {SILVER_TB_CLIENTES}
    ALTER COLUMN fecha_nacimiento SET TAGS ("PII")
    """
    )

# COMMAND ----------

spark.sql(
    f"""
    ALTER TABLE {SILVER_TB_CLIENTES}
    ALTER COLUMN genero SET TAGS ("sensible")
    """
    )