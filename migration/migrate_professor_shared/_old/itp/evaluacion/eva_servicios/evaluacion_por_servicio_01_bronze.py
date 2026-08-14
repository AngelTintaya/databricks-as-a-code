# Databricks notebook source
my_catalog = 'g3_eva_servicios'

# COMMAND ----------

spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.bronze.tb_catalogo_servicios""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.bronze.tb_ordenes_det""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.bronze.tb_sedes""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.bronze.tb_metas""")

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {my_catalog}.bronze.tb_catalogo_servicios
    COMMENT "Esta tabla contiene el catálogo de servicios."
    AS
    SELECT *, current_timestamp() AS inserted_at
    FROM read_files(
        'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G3/catalogo_servicios_20251108.csv',
        format => 'csv',
        header => false,
        delimiter => ';',
        inferSchema => true
        --schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
        )
    """
)

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {my_catalog}.bronze.tb_ordenes_det
    COMMENT "Esta tabla contiene los detalles de las órdenes de servicio."
    AS
    SELECT *, current_timestamp() AS inserted_at
    FROM read_files(
        'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G3/ordenes_detalles_20251103.csv',
        format => 'csv',
        header => false,
        delimiter => ';',
        inferSchema => true
        --schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
        )
    """
)

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.bronze.tb_catalogo_servicios""").display()

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.bronze.tb_ordenes_det""").display()