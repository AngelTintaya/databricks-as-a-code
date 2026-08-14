# Databricks notebook source
from pyspark.sql.functions import to_date
from pyspark.sql.functions import col, lit
from datetime import datetime, date

# COMMAND ----------

# dbutils.widgets.text('STR_INGESTION_DATE', '2025-05-01')

# COMMAND ----------

STR_INGESTION_DATE = dbutils.widgets.get("STR_INGESTION_DATE")
INGESTION_DATE = datetime.strptime(STR_INGESTION_DATE, '%Y-%m-%d').date() if STR_INGESTION_DATE else date.today()

# COMMAND ----------

INGESTION_DATE

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
          FROM g0_mkt_clientes.bronze.raw_clientes
          WHERE to_date(inserted_at) = '{INGESTION_DATE}'
          """)

# COMMAND ----------

spark.sql("""
          MERGE INTO g0_mkt_clientes.silver.clientes cli
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
          """)