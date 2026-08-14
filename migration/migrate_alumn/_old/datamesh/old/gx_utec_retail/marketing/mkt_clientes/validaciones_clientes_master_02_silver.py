# Databricks notebook source
from pyspark.sql.functions import to_date
from pyspark.sql.functions import col, lit
from datetime import datetime, date

# COMMAND ----------

dbutils.widgets.text('STR_INGESTION_DATE', '2025-05-01')

# COMMAND ----------

STR_INGESTION_DATE = dbutils.widgets.get("STR_INGESTION_DATE")
INGESTION_DATE = datetime.strptime(STR_INGESTION_DATE, '%Y-%m-%d').date() if STR_INGESTION_DATE else date.today()

# COMMAND ----------

INGESTION_DATE

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
          FROM g0_mkt_clientes.bronze.raw_clientes
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

spark.sql("""
          INSERT INTO g0_mkt_clientes.support.errores_validacion (process, total_errores, tipo_error, created_at)
          SELECT process, total_errores, tipo_error, created_at FROM errores_validacion
          """)

# COMMAND ----------

spark.sql("""
          INSERT INTO g0_mkt_clientes.support.cuarentena_raw_clientes
          SELECT cliente_id, nombre, email, fecha_nacimiento, genero, ubicacion, fecha, inserted_at
          FROM g0_mkt_clientes.bronze.raw_clientes
          """)

# COMMAND ----------

raise Exception("Se encontraron errores de validación. Ver tabla g0_mkt_clientes.support.errores_validacion.")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM errores_validacion