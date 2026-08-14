# Databricks notebook source
# MAGIC %run /Shared/data_platform/data_contracts

# COMMAND ----------

help(get_data_contract)

# COMMAND ----------

[t.name for t in spark.catalog.listTables("gx00_cmc_ventas.gold")]

# COMMAND ----------

# MAGIC %md
# MAGIC # Data Contract: Ventas

# COMMAND ----------

data_contract = get_data_contract(
    catalog_name = 'gx00_cmc_ventas',
    schema_name = 'gold',
    table_name = 'vw_ventas',
    data_product_name = 'ventas',
    domain_name = 'comercial',
    owner_email = 'angel.tintaya@utec.edu.pe',
    freshness = 'updated_daily',
    rules_field_not_null = ['venta_id', 'cliente_id', 'producto_id'],
    rules_field_email = None,
    rules_field_dob = None
    )

# COMMAND ----------

print(data_contract)

# COMMAND ----------

# MAGIC %md
# MAGIC # Data Contract: Ventas por Canal

# COMMAND ----------

data_contract = get_data_contract(
    catalog_name = 'gx00_cmc_ventas',
    schema_name = 'gold',
    table_name = 'vw_ventas_por_canal',
    data_product_name = 'ventas',
    domain_name = 'comercial',
    owner_email = 'angel.tintaya@utec.edu.pe',
    freshness = 'updated_daily',
    rules_field_not_null = ['fecha_venta'],
    rules_field_email = None,
    rules_field_dob = None
    )

# COMMAND ----------

print(data_contract)

# COMMAND ----------

# MAGIC %md
# MAGIC # Data Contract: Ventas por Producto

# COMMAND ----------

data_contract = get_data_contract(
    catalog_name = 'gx00_cmc_ventas',
    schema_name = 'gold',
    table_name = 'vw_ventas_por_producto',
    data_product_name = 'ventas',
    domain_name = 'comercial',
    owner_email = 'angel.tintaya@utec.edu.pe',
    freshness = 'updated_daily',
    rules_field_not_null = ['fecha_venta', 'producto_id'],
    rules_field_email = None,
    rules_field_dob = None
    )

# COMMAND ----------

print(data_contract)