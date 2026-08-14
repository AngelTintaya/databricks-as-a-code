# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook **will run** in Pipeline
# MAGIC - Will validate data from BRONZE_TB_RAW_CLIENTES
# MAGIC - If data is not valid, will INSERT data into SUPPORT_TB_ERRORES_VALIDACION, SUPPORT_TB_CUARENTENA_RAW_CLIENTES
# MAGIC - COMMENT widget creation: dbutils.widgets.text() -> It will be created in the pipeline

# COMMAND ----------

# MAGIC %run ./__clientes_parameter

# COMMAND ----------

from pyspark.sql.functions import to_date
from datetime import datetime, date

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dataproduct Parameters

# COMMAND ----------

dict_tables = get_medallion_tables()
BRONZE_TB_RAW_CLIENTES = dict_tables.get('BRONZE_TB_RAW_CLIENTES')

# COMMAND ----------

print('BRONZE_TB_RAW_CLIENTES\t:', BRONZE_TB_RAW_CLIENTES)

# COMMAND ----------

dict_support_tables = get_support_tables()
SUPPORT_TB_ERRORES_VALIDACION = dict_support_tables.get('SUPPORT_TB_ERRORES_VALIDACION')
SUPPORT_TB_CUARENTENA_RAW_CLIENTES = dict_support_tables.get('SUPPORT_TB_CUARENTENA_RAW_CLIENTES')

# COMMAND ----------

print('SUPPORT_TB_ERRORES_VALIDACION\t\t:', SUPPORT_TB_ERRORES_VALIDACION)
print('SUPPORT_TB_CUARENTENA_RAW_CLIENTES\t:', SUPPORT_TB_CUARENTENA_RAW_CLIENTES)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pipeline Parameters

# COMMAND ----------

# dbutils.widgets.text('STR_INGESTION_DATE', '2025-05-01')

# COMMAND ----------

STR_INGESTION_DATE = dbutils.widgets.get("STR_INGESTION_DATE")
INGESTION_DATE = datetime.strptime(STR_INGESTION_DATE, '%Y-%m-%d').date() if STR_INGESTION_DATE else date.today()

# COMMAND ----------

print('STR_INGESTION_DATE\t:', STR_INGESTION_DATE)
print('INGESTION_DATE\t\t:', INGESTION_DATE)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Process

# COMMAND ----------

spark.sql(f"""
          CREATE OR REPLACE TEMPORARY VIEW data_a_validar
          AS
          SELECT
            cliente_id,
            nombre,
            email,
            fecha_nacimiento,
            genero,
            ubicacion,
            fecha,
            inserted_at
          FROM {BRONZE_TB_RAW_CLIENTES}
          WHERE to_date(inserted_at) = '{INGESTION_DATE}'
          """)

# COMMAND ----------

spark.sql(f"""
          CREATE OR REPLACE TEMPORARY VIEW errores_id_nulo AS
          SELECT
            COUNT(*) AS total_errores,
            'errores_id_nulo' AS tipo_error,
            CAST('{INGESTION_DATE}' AS DATE) as created_at
          FROM data_a_validar
          WHERE cliente_id IS NULL
          """)

# COMMAND ----------

spark.sql(f"""
          CREATE OR REPLACE TEMPORARY VIEW errores_formato_email AS
          SELECT
            COUNT(*) AS total_errores,
            'errores_formato_email' AS tipo_error,
            CAST('{INGESTION_DATE}' AS DATE) as created_at
          FROM data_a_validar
          WHERE email IS NOT NULL
          AND email NOT LIKE '%@%.%'
          """)

# COMMAND ----------

spark.sql(f"""
          CREATE OR REPLACE TEMPORARY VIEW errores_email_nulos AS
          WITH counts AS (
              SELECT
                COUNT(*) AS total_count,
                COUNT(CASE WHEN email IS NULL THEN 1 END) AS email_null_count
              FROM data_a_validar
          )
          SELECT
            COUNT(CASE WHEN email_null_count > (0.1 * total_count) THEN 1 END) AS total_errores,
            'errores_email_nulos' AS tipo_error,
            CAST('{INGESTION_DATE}' AS DATE) as created_at
          FROM counts          
          """)

# COMMAND ----------

spark.sql(f"""
          CREATE OR REPLACE TEMPORARY VIEW errores_validacion AS
          SELECT 'clientes_master' AS process, total_errores, tipo_error, created_at FROM errores_id_nulo
          UNION ALL
          SELECT 'clientes_master' AS process, total_errores, tipo_error, created_at FROM errores_formato_email
          UNION ALL
          SELECT 'clientes_master' AS process, total_errores, tipo_error, created_at FROM errores_email_nulos
          """)

# COMMAND ----------

df_errores = spark.sql(
    """
    SELECT COUNT(*) as total_errores
    FROM errores_validacion
    WHERE total_errores > 0
    """
    )
total_errores = df_errores.collect()[0][0]

if total_errores == 0:
    dbutils.notebook.exit("No se encontraron errores de validación.")

# COMMAND ----------

spark.sql(f"""
    DELETE FROM {SUPPORT_TB_ERRORES_VALIDACION}
    WHERE created_at = DATE('{INGESTION_DATE}')
""")

# COMMAND ----------

spark.sql(f"""
          INSERT INTO {SUPPORT_TB_ERRORES_VALIDACION} (process, total_errores, tipo_error, created_at)
          SELECT process, total_errores, tipo_error, created_at FROM errores_validacion
          """)

# COMMAND ----------

spark.sql(f"""
    DELETE FROM {SUPPORT_TB_CUARENTENA_RAW_CLIENTES}
    WHERE inserted_at = DATE('{INGESTION_DATE}')
""")

# COMMAND ----------

spark.sql(f"""
          INSERT INTO {SUPPORT_TB_CUARENTENA_RAW_CLIENTES}
          SELECT
            cliente_id, nombre, email, fecha_nacimiento, genero, ubicacion, fecha, inserted_at
          FROM {BRONZE_TB_RAW_CLIENTES}
          """)

# COMMAND ----------

raise Exception(f"Se encontraron errores de validación. Ver tabla {SUPPORT_TB_ERRORES_VALIDACION}.")