# Databricks notebook source
# MAGIC %run /Shared/data_platform/data_contracts

# COMMAND ----------

help(get_data_contract)

# COMMAND ----------

[t.name for t in spark.catalog.listTables("gx00_ops_productos.gold")]

# COMMAND ----------

# MAGIC %md
# MAGIC # Data Contract: Inventario

# COMMAND ----------

data_contract = get_data_contract(
    catalog_name = 'gx00_ops_productos',
    schema_name = 'gold',
    table_name = 'vw_inventario',
    data_product_name = 'inventario',
    domain_name = 'operaciones',
    owner_email = 'angel.tintaya@utec.edu.pe',
    freshness = 'updated_monthly',
    rules_field_not_null = ['producto_id'],
    rules_field_email = None,
    rules_field_dob = None
    )

# COMMAND ----------

print(data_contract)

# COMMAND ----------

# MAGIC %md
# MAGIC # Data Contract: HM Product Performance

# COMMAND ----------

data_contract = get_data_contract(
    catalog_name = 'gx00_ops_productos',
    schema_name = 'gold',
    table_name = 'vw_hm_producto_performance',
    data_product_name = 'inventario',
    domain_name = 'operaciones',
    owner_email = 'angel.tintaya@utec.edu.pe',
    freshness = 'updated_monthly',
    rules_field_not_null = ['producto_id'],
    rules_field_email = None,
    rules_field_dob = None
    )

# COMMAND ----------

print(data_contract)

# COMMAND ----------

# MAGIC %md
# MAGIC # Data Contract: UM Product Performance

# COMMAND ----------

data_contract = get_data_contract(
    catalog_name = 'gx00_ops_productos',
    schema_name = 'gold',
    table_name = 'vw_um_producto_performance',
    data_product_name = 'inventario',
    domain_name = 'operaciones',
    owner_email = 'angel.tintaya@utec.edu.pe',
    freshness = 'updated_monthly',
    rules_field_not_null = ['producto_id'],
    rules_field_email = None,
    rules_field_dob = None
    )

# COMMAND ----------

print(data_contract)