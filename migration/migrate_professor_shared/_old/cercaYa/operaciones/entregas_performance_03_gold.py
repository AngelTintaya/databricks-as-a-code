# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook will NOT run in Pipeline
# MAGIC - Views only needs to be created the first time

# COMMAND ----------

my_catalog = 'g204_ops_entregas'

# COMMAND ----------

dbutils.widgets.text('SILVER_VW_ENVIOS_GEO', f'{my_catalog}.silver.vw_envios_geo')
dbutils.widgets.text('GOLD_VW_ALERTAS_RETRASOS', f'{my_catalog}.gold.vw_alertas_retrasos')
dbutils.widgets.text('GOLD_VW_KPIS_DARK_STORE', f'{my_catalog}.gold.vw_kpis_entregas_por_dark_store')

# COMMAND ----------

SILVER_VW_ENVIOS_GEO = dbutils.widgets.get("SILVER_VW_ENVIOS_GEO")
GOLD_VW_ALERTAS_RETRASOS = dbutils.widgets.get("GOLD_VW_ALERTAS_RETRASOS")
GOLD_VW_KPIS_DARK_STORE = dbutils.widgets.get("GOLD_VW_KPIS_DARK_STORE")

# COMMAND ----------

print('SILVER_VW_ENVIOS_GEO\t\t:', SILVER_VW_ENVIOS_GEO)
print('GOLD_VW_ALERTAS_RETRASOS\t:', GOLD_VW_ALERTAS_RETRASOS)
print('GOLD_VW_KPIS_DARK_STORE\t\t:', GOLD_VW_KPIS_DARK_STORE)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {GOLD_VW_ALERTAS_RETRASOS}
    (
        envio_id COMMENT 'Identificador único del envío',
        zona_id COMMENT 'Código único de la zona o punto de origen',
        tiempo_entrega_min COMMENT 'Tiempo real final tomado para completar la entrega en minutos',
        minutos_retraso COMMENT 'Diferencia en minutos de exceso sobre el SLA de tiempo (asumiendo SLA de 30 min)',
        criticidad_alerta COMMENT 'Nivel de criticidad basado en los minutos de retraso (Alta, Media, Baja)',
        fecha_operacion COMMENT 'Fecha en la que ocurrió el despacho'
    )
    COMMENT 'Vista de control operativo que consolida todos los despachos con entregas retrasadas fuera de SLA'
    AS
    SELECT
        envio_id,
        zona_id,
        tiempo_entrega_min,
        (tiempo_entrega_min - 30) AS minutos_retraso,
        CASE 
            WHEN (tiempo_entrega_min - 30) > 30 THEN 'Alta'
            WHEN (tiempo_entrega_min - 30) > 15 THEN 'Media'
            ELSE 'Baja'
        END AS criticidad_alerta,
        CAST(inserted_at AS DATE) AS fecha_operacion
    FROM {SILVER_VW_ENVIOS_GEO}
    WHERE estado_entrega = 'RETRASADO'
    """
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW {GOLD_VW_KPIS_DARK_STORE}
    (
        cod_mes COMMENT 'Periodo mensual del análisis en formato YYYYMM',
        zona_id COMMENT 'Identificador único de la zona o sede',
        total_despachos COMMENT 'Cantidad total de órdenes distribuidas',
        efectividad_entrega_pct COMMENT 'Porcentaje de entregas completadas a tiempo con base en el total',
        promedio_espera_mins COMMENT 'Tiempo promedio ponderado de despacho de la sede'
    )
    COMMENT 'Métricas mensuales acumuladas de efectividad de entrega y niveles de servicio por sucursal'
    AS
    SELECT
        cod_mes,
        zona_id,
        COUNT(DISTINCT envio_id) AS total_despachos,
        ROUND((COUNT(CASE WHEN estado_entrega = 'A TIEMPO' THEN 1 END) / COUNT(DISTINCT envio_id)) * 100, 2) AS efectividad_entrega_pct,
        ROUND(AVG(tiempo_entrega_min), 2) AS promedio_espera_mins
    FROM {SILVER_VW_ENVIOS_GEO}
    GROUP BY
        cod_mes,
        zona_id
    """
)