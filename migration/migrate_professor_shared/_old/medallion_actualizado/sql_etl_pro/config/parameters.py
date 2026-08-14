# Databricks notebook source
# DBTITLE 1,Define parameters
params = {
    'catalog': 'gx_catalog',
    'prefix': 'atm',
    'source_path': 'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/input_pro.csv'
}
print('Dictionary imported: params')