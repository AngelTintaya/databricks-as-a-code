# Databricks notebook source
# Remove a folder recursively
dbutils.fs.rm('abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/ventas', recurse=True)

# COMMAND ----------

# Create folders
dbutils.fs.mkdirs('abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/clientes',)
dbutils.fs.mkdirs('abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/ventas/ecommerce',)
dbutils.fs.mkdirs('abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/ventas/tienda',)
dbutils.fs.mkdirs('abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/productos/inventario',)

# COMMAND ----------

# Move files
dbutils.fs.mv(
    'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/inventario.csv',
    'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/productos/inventario/'
    )