# Databricks notebook source
my_catalog = 'g204_ops_entregas'

# COMMAND ----------

BRONZE_TB_RAW_ENVIOS = f'{my_catalog}.bronze.raw_envios'
SILVER_TB_UM_PROD_PERF = f'{my_catalog}.silver.um_producto_performance'
SILVER_TB_HM_PROD_PERF = f'{my_catalog}.silver.hm_producto_performance'

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {BRONZE_TB_RAW_ENVIOS}')

# COMMAND ----------

spark.sql(
f"""
    CREATE OR REPLACE TABLE {BRONZE_TB_RAW_ENVIOS} (
      envio_id STRING COMMENT 'Identificador único del envío',
      venta_id STRING COMMENT 'Identificador de la venta asociada',
      repartidor_id STRING COMMENT 'Identificador único del repartidor',
      distrito_entrega STRING COMMENT 'Distrito geográfico de destino',
      fecha_envio STRING COMMENT 'Fecha en que se despachó el envío',
      hora_asignacion STRING COMMENT 'Hora de asignación al repartidor',
      hora_entrega STRING COMMENT 'Hora final de entrega al cliente',
      tiempo_entrega_min DOUBLE COMMENT 'Tiempo transcurrido en minutos para la entrega',
      estado_entrega STRING COMMENT 'Estado actual del envío (Entregado, Pendiente, Cancelado)',
      distancia_km DOUBLE COMMENT 'Distancia recorrida en kilómetros',
      calificacion_cliente DOUBLE COMMENT 'Puntuación otorgada por el cliente',
      inserted_at TIMESTAMP COMMENT 'Timestamp de inserción en la capa Bronze'
    )
    COMMENT 'Tabla raw para la ingesta de envíos y operaciones'
    CLUSTER BY (fecha_envio)
    """
)

# COMMAND ----------

spark.sql(f'OPTIMIZE {SILVER_TB_HM_PROD_PERF}')

# COMMAND ----------

spark.sql(f'DESCRIBE HISTORY {SILVER_TB_HM_PROD_PERF}').display()