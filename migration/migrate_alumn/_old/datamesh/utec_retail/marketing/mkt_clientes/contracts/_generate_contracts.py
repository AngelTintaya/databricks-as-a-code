# Databricks notebook source
# MAGIC %run /Shared/data_platform/data_contracts

# COMMAND ----------

help(get_data_contract)

# COMMAND ----------

[t.name for t in spark.catalog.listTables("g0_mkt_clientes.gold")]

# COMMAND ----------

# MAGIC %md
# MAGIC # Data Contract: Clientes

# COMMAND ----------

data_contract = get_data_contract(
    catalog_name = 'g0_mkt_clientes',
    schema_name = 'gold',
    table_name = 'vw_clientes',
    data_product_name = 'clientes',
    domain_name = 'marketing',
    owner_email = 'angel.tintaya@utec.edu.pe',
    freshness = 'updated_monthly',
    rules_field_not_null = ['cliente_id'],
    rules_field_email = ['email'],
    rules_field_dob = ['fecha_nacimiento']
    )

# COMMAND ----------

print(data_contract)

# COMMAND ----------

# MAGIC %md
# MAGIC # Data Contract: Clientes Perfil

# COMMAND ----------

data_contract = get_data_contract(
    catalog_name = 'g0_mkt_clientes',
    schema_name = 'gold',
    table_name = 'vw_clientes_perfil',
    data_product_name = 'clientes',
    domain_name = 'marketing',
    owner_email = 'angel.tintaya@utec.edu.pe',
    freshness = 'updated_monthly',
    rules_field_not_null = ['cliente_id'],
    rules_field_email = ['email'],
    rules_field_dob = ['fecha_nacimiento']
    )

# COMMAND ----------

print(data_contract)