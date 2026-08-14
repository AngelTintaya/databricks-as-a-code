# Databricks notebook source
import json

# COMMAND ----------

MY_GROUP = 'gx00'

# COMMAND ----------

def get_paths():
    return {
        'INPUT_PATH': 'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/clientes/',
        'SCHEMA_PATH': 'abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/G0/clientes/_schemas',
        'CHECKPOINT_PATH': 'abfss://datalake@stdemdsai.dfs.core.windows.net/_checkpoints/g0/clientes'
        }


# COMMAND ----------

def get_medallion_tables():
    return {
        'BRONZE_TB_RAW_CLIENTES': f'{MY_GROUP}_mkt_clientes.bronze.raw_clientes',
        'SILVER_TB_CLIENTES': f'{MY_GROUP}_mkt_clientes.silver.clientes',
        'GOLD_VW_CLIENTES': f'{MY_GROUP}_mkt_clientes.gold.vw_clientes',
        'SILVER_MV_CLIENTES_PERFIL': f'{MY_GROUP}_mkt_clientes.silver.mv_clientes_perfil',
        'GOLD_VW_CLIENTES_PERFIL': f'{MY_GROUP}_mkt_clientes.gold.vw_clientes_perfil',
        'GOLD_VW_VENTAS': f'{MY_GROUP}_cmc_ventas.gold.vw_ventas'
    }

# COMMAND ----------

def get_support_tables():
    return {
        'SUPPORT_TB_ERRORES_VALIDACION': f'{MY_GROUP}_mkt_clientes.support.errores_validacion',
        'SUPPORT_TB_CUARENTENA_RAW_CLIENTES': f'{MY_GROUP}_mkt_clientes.support.cuarentena_raw_clientes'
    }

# COMMAND ----------

print(json.dumps({
    'get_paths()': 'Get all paths parameters',
    'get_medallion_tables()': 'Get all medallion tables parameters',
    'get_support_tables()': 'Get all support tables parameters'
    }, indent=4))