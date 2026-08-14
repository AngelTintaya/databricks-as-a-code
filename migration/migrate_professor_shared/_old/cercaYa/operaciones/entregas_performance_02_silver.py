# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook **WILL RUN** in Pipeline
# MAGIC - Need to create temporary views and insert into SILVER_TB_HM_PROD_PERF silver table
# MAGIC - Need to create SILVER_TB_UM_PROD_PERF silver table on top of SILVER_TB_HM_PROD_PERFsilver table.
# MAGIC - COMMENT widget creation: dbutils.widgets.text() -> It will be created in the pipeline

# COMMAND ----------

from datetime import datetime
from dateutil.relativedelta import relativedelta

# COMMAND ----------

my_catalog = 'g204_ops_entregas'

# COMMAND ----------

# dbutils.widgets.text('GOLD_VW_VENTAS', f'{my_group}_cmc_ventas.gold.vw_ventas')
# dbutils.widgets.text('BRONZE_TB_RAW_ENVIOS', f'{my_group}_cmc_demanda_zonal.bronze.raw_envios')
# dbutils.widgets.text('SILVER_VW_ENVIOS_GEO', f'{my_group}_cmc_demanda_zonal.silver.vw_envios_geo')
# dbutils.widgets.text('FECHA_ACTUAL', '2026-07-01')

# COMMAND ----------

BRONZE_TB_RAW_ENVIOS = f'{my_catalog}.bronze.raw_envios'
SILVER_VW_VENTAS     = f'{my_catalog}.silver.vw_ventas'
SILVER_VW_ENVIOS_GEO = f'{my_catalog}.silver.vw_envios_geo'

# COMMAND ----------

# Recuperamos el valor si el widget existe (Airflow), si no, manejamos el error asignando None
try:
    STR_INGESTION_DATE = dbutils.widgets.get("STR_INGESTION_DATE")
except Exception:
    STR_INGESTION_DATE = None

# Si no hay fecha del widget, usamos una fecha por defecto para desarrollo (ej: 2026-07-17)
if not STR_INGESTION_DATE:
    STR_INGESTION_DATE = "2026-07-17"

# Formateamos la fecha base
FECHA_ACTUAL_DT = datetime.strptime(STR_INGESTION_DATE, '%Y-%m-%d')

# COMMAND ----------

CODMES_ANTERIOR = (FECHA_ACTUAL_DT - relativedelta(months=1)).strftime('%Y%m')

# COMMAND ----------

print('BRONZE_TB_RAW_ENVIOS\t:', BRONZE_TB_RAW_ENVIOS)
print('SILVER_VW_VENTAS\t\t:', SILVER_VW_VENTAS)
print('SILVER_VW_ENVIOS_GEO\t:', SILVER_VW_ENVIOS_GEO)
print('CODMES_ANTERIOR\t\t:', CODMES_ANTERIOR)

# COMMAND ----------

spark.sql(
  f"""
  CREATE OR REPLACE TEMPORARY VIEW envios_mes_temp AS
    SELECT
      e.envio_id,
      e.venta_id,
      e.repartidor_id,
      e.distrito_entrega AS zona_id,
      e.fecha_envio,
      e.estado_entrega,
      e.tiempo_entrega_min,
      e.distancia_km,
      DATE_FORMAT(TO_DATE(e.fecha_envio), 'yyyyMM') AS cod_mes
    FROM {BRONZE_TB_RAW_ENVIOS} e
    WHERE DATE_FORMAT(TO_DATE(e.fecha_envio), 'yyyyMM') = {CODMES_ANTERIOR}
  """
)

# COMMAND ----------

spark.sql(f"""
    CREATE OR REPLACE VIEW {SILVER_VW_VENTAS}
    COMMENT 'Vista de la capa Silver que estructura la información de ventas originadas en operaciones'
    AS
    SELECT
        DATE_FORMAT(TO_DATE(fecha_envio), 'yyyyMM') AS cod_mes,
        venta_id,
        envio_id,
        distrito_entrega AS zona_id,
        estado_entrega
    FROM {BRONZE_TB_RAW_ENVIOS}
    WHERE DATE_FORMAT(TO_DATE(fecha_envio), 'yyyyMM') = {CODMES_ANTERIOR}
""")

# COMMAND ----------

spark.sql(
    f"DELETE FROM {SILVER_VW_ENVIOS_GEO} WHERE periodo = {CODMES_ANTERIOR}"
)

# COMMAND ----------

spark.sql(f"""
    CREATE OR REPLACE VIEW {SILVER_VW_ENVIOS_GEO}
    COMMENT 'Vista final de la capa Silver que consolida geografía y logística'
    AS
    SELECT
        DATE_FORMAT(TO_DATE(fecha_envio), 'yyyyMM') AS cod_mes,
        venta_id,
        envio_id,
        distrito_entrega AS zona_id,
        estado_entrega,
        tiempo_entrega_min,
        distancia_km,
        current_timestamp() AS inserted_at
    FROM {BRONZE_TB_RAW_ENVIOS}
    WHERE DATE_FORMAT(TO_DATE(fecha_envio), 'yyyyMM') = {CODMES_ANTERIOR}
""")