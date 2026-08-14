# Databricks notebook source
BRONZE_TB_RAW_INVENTARIO = 'ga_ops_productos.bronze.raw_inventario'
SILVER_TB_UM_PROD_PERF = 'ga_ops_productos.silver.um_producto_performance'
SILVER_TB_HM_PROD_PERF = 'ga_ops_productos.silver.hm_producto_performance'

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {BRONZE_TB_RAW_INVENTARIO}')

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {SILVER_TB_UM_PROD_PERF}')

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {SILVER_TB_HM_PROD_PERF}')

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {BRONZE_TB_RAW_INVENTARIO} (
      codmes STRING COMMENT 'Código del mes en que se realizó el inventario (Formato YYYYMM)',
      producto_id STRING COMMENT 'Identificador único del producto',
      producto_nombre STRING COMMENT 'Nombre del producto',
      stock INT COMMENT 'Stock actual del producto',
      tienda STRING COMMENT 'Tienda en que se encuentra el producto',
      creado TIMESTAMP COMMENT 'Timestamp en que se creó el registro',
      _rescued_data STRING COMMENT 'Datos adicionales o no estructurados rescatados durante la ingesta',
      inserted_at TIMESTAMP COMMENT 'Timestamp en que se insertó este snapshot'
    )
    COMMENT 'Tabla raw del invetario de productos'
    """
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {SILVER_TB_HM_PROD_PERF} (
        periodo STRING COMMENT 'Periodo de tiempo mensual en el que se calculó el performance',
        producto_id STRING COMMENT 'Identificador único del producto',
        producto_nombre STRING COMMENT 'Nombre del producto',
        total_ventas INT COMMENT 'Total de unidades vendidas en el periodo',
        stock_actual INT COMMENT 'Stock actual al cierre del periodo',
        rotacion DOUBLE COMMENT 'Ratio de rotación del producto en el periodo calculado como total_ventas / stock_actual.',
        ranking_rotacion INT COMMENT 'Ranking dentro del mes por rotación, orden descendente.',
        inserted_at TIMESTAMP COMMENT 'Timestamp en que se insertó este snapshot'
    )
    COMMENT 'Tabla histórica mensual con indicadores de performance de productos'
    CLUSTER BY (periodo, producto_id)
    """
)

# COMMAND ----------

spark.sql(f'OPTIMIZE {SILVER_TB_HM_PROD_PERF}')

# COMMAND ----------

spark.sql(f'DESCRIBE HISTORY {SILVER_TB_HM_PROD_PERF}').display()