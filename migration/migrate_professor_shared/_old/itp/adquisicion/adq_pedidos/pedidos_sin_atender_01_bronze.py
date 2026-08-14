# Databricks notebook source
my_catalog = 'g3_adq_pedidos'

# COMMAND ----------

spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.bronze.tb_pedidos""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.bronze.tb_ordenes""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.bronze.tb_sedes""")
spark.sql(f"""DROP TABLE IF EXISTS {my_catalog}.bronze.tb_metas""")

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {my_catalog}.bronze.tb_pedidos
    COMMENT "Esta tabla contiene los pedidos de servicio."
    AS
    SELECT *, current_timestamp() AS inserted_at
    FROM read_files(
        'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G3/pedidos_20251108.csv',
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
    CREATE OR REPLACE TABLE {my_catalog}.bronze.tb_ordenes
    COMMENT "Esta tabla contiene las órdenes de servicio."
    AS
    SELECT *, current_timestamp() AS inserted_at
    FROM read_files(
        'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G3/ordenes_20251108.csv',
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
    CREATE OR REPLACE TABLE {my_catalog}.bronze.tb_sedes
    COMMENT "Esta tabla contiene las sedes de la entidad."
    AS
    SELECT *, current_timestamp() AS inserted_at
    FROM read_files(
        'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G3/sedes_20251103.csv',
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
    CREATE OR REPLACE TABLE {my_catalog}.bronze.tb_metas
    COMMENT "Esta tabla contiene las metas de gestión."
    AS
    SELECT *, current_timestamp() AS inserted_at
    FROM read_files(
        'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G3/metas_20251108.csv',
        format => 'csv',
        header => false,
        delimiter => ';',
        inferSchema => true
        --schema => 'id INT, producto STRING, cantidad INT, precio DOUBLE'
        )
    """
)

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.bronze.tb_pedidos""").display()

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.bronze.tb_ordenes""").display()

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.bronze.tb_sedes""").display()

# COMMAND ----------

spark.sql(f"""SELECT * FROM {my_catalog}.bronze.tb_metas""").display()