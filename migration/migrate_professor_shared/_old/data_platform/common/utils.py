# Databricks notebook source
# MAGIC %run ./_params

# COMMAND ----------

def generate_dataproduct(domain, dp_name, action='create'):
    data_product = {
        'name': dp_name,
        'catalog_name': f'{domain["code"]}_{dp_name}',
        'description': f'Data product de clientes del dominio de {domain["name"]}'
        }

    if action == 'create':
        spark.sql(f"""CREATE CATALOG IF NOT EXISTS {data_product["catalog_name"]} COMMENT '{data_product["description"]}'""")

        for name_schema, desc_schema in schema_descriptions.items():
            schema_name = f'{data_product["catalog_name"]}.{name_schema}'
            spark.sql(f'CREATE SCHEMA IF NOT EXISTS {schema_name} COMMENT "{desc_schema}"')
            spark.sql(f'ALTER SCHEMA {schema_name} OWNER TO `{admin}`')

        spark.sql(f'ALTER CATALOG {data_product["catalog_name"]} OWNER TO `{admin}`')
        print(f'Se creó el data product {data_product["catalog_name"]}')
    
    elif action == 'delete':
        for name_schema in schema_descriptions.keys():
            schema_name = f'{data_product["catalog_name"]}.{name_schema}'
            spark.sql(f'DROP SCHEMA IF EXISTS {schema_name} CASCADE')
        
        spark.sql(f'DROP SCHEMA IF EXISTS default CASCADE')
        spark.sql(f'DROP CATALOG IF EXISTS {data_product["catalog_name"]} CASCADE')
        print(f'Se eliminó el data product {data_product["catalog_name"]}')

# COMMAND ----------

# Creates groups:
## Reader (<catalog_name>_reader)
## Writer (<catalog_name>_writer)
## Admin (<catalog_name>_admin). 
# Grant access to each group to its respective catalog
## In _params we have privileges
# Add list of users to each group
## Team leader: Admin
## Team members: Writer
## utec-de group: Reader