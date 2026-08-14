# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook **will run** in Pipeline
# MAGIC - Need to create temporary views from BRONZE_TB_RAW_CLIENTES and MERGE into SILVER_TB_CLIENTES table
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
SILVER_TB_CLIENTES = dict_tables.get('SILVER_TB_CLIENTES')

# COMMAND ----------

print('BRONZE_TB_RAW_CLIENTES\t:', BRONZE_TB_RAW_CLIENTES)
print('SILVER_TB_CLIENTES\t:', SILVER_TB_CLIENTES)

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
          CREATE OR REPLACE TEMPORARY VIEW nuevos_clientes
          AS
          SELECT
            cliente_id,
            INITCAP(nombre) AS nombre,
            email,
            fecha_nacimiento,
            genero,
            INITCAP(ubicacion) AS ciudad,
            CAST(fecha AS TIMESTAMP) as created_at,
            inserted_at
          FROM {BRONZE_TB_RAW_CLIENTES}
          WHERE to_date(inserted_at) = '{INGESTION_DATE}'
          """)

# COMMAND ----------

spark.sql(f"""
          MERGE INTO {SILVER_TB_CLIENTES} cli
          USING nuevos_clientes raw ON cli.cliente_id = raw.cliente_id
          WHEN MATCHED THEN UPDATE SET
            cli.nombre = raw.nombre,
            cli.email = raw.email,
            cli.fecha_nacimiento = raw.fecha_nacimiento,
            cli.genero = raw.genero,
            cli.ciudad = raw.ciudad,
            cli.created_at = raw.created_at,
            cli.inserted_at = raw.inserted_at
          WHEN NOT MATCHED THEN INSERT
          (cliente_id, nombre, email, fecha_nacimiento, genero, ciudad, created_at, inserted_at)
          VALUES
          (raw.cliente_id, raw.nombre, raw.email, raw.fecha_nacimiento, raw.genero, raw.ciudad, raw.created_at, current_timestamp())
          """).display()