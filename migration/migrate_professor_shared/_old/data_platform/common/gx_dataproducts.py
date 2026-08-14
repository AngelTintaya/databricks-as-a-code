# Databricks notebook source
# MAGIC %run ./utils

# COMMAND ----------

group = 'gx'
domains_dps = [
    ({'code': f'{group}_cmc', 'name': 'comercial'}, 'ventas'),
    ({'code': f'{group}_ops', 'name': 'operaciones', }, 'productos'),
    ({'code': f'{group}_mkt', 'name': 'marketing', }, 'clientes'),
]

for domain, dp_name in domains_dps:
    generate_dataproduct(domain, dp_name)
    # generate_dataproduct(domain, dp_name, action='delete')