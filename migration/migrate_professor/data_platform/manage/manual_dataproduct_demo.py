# Databricks notebook source
# MAGIC %md
# MAGIC ## Manual Data Product Creation — Step by Step
# MAGIC This notebook shows every step to create a data product in Unity Catalog.
# MAGIC Run each cell individually and observe the result before moving to the next.

# COMMAND ----------

# MAGIC %md ### Configuration

# COMMAND ----------

group       = 'gx00'
domain_code = 'mkt'
domain_name = 'marketing'
dp_name     = 'clientes'
leader      = 'atintaya@utec.edu.pe'
members     = ['angel.tintaya@utec.edu.pe']

catalog_name = f'{group}_{domain_code}_{dp_name}'
print(f"Catalog to be created: {catalog_name}")

# COMMAND ----------

# MAGIC %md ### Step 1 — Create Catalog

# COMMAND ----------

spark.sql(f"""
    CREATE CATALOG IF NOT EXISTS {catalog_name}
    COMMENT 'Data product de {dp_name} del dominio de {domain_name}'
""")
spark.sql(f"SHOW CATALOGS LIKE '{catalog_name}'").display()

# COMMAND ----------

# MAGIC %md ### Step 2 — Create Schemas (Medallion Architecture)

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog_name}.bronze COMMENT 'Raw data schema'")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog_name}.silver COMMENT 'Cleaned data schema'")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog_name}.gold   COMMENT 'Aggregated data schema'")
spark.sql(f"SHOW SCHEMAS IN {catalog_name}").display()

# COMMAND ----------

# MAGIC %md ### Step 3 — Create Groups in the UI
# MAGIC Go to **Settings → Identity and Access → Groups → Add Group** and create the following three account-level groups:
# MAGIC - `{catalog_name}_reader` (e.g. `gx_mkt_clientes_reader`)
# MAGIC - `{catalog_name}_writer` (e.g. `gx_mkt_clientes_writer`)
# MAGIC - `{catalog_name}_admin`  (e.g. `gx_mkt_clientes_admin`)
# MAGIC
# MAGIC Make sure each group is assigned to this workspace before continuing.

# COMMAND ----------

# MAGIC %md ### Step 4 — Grant Privileges on Catalog
# MAGIC Run this after the groups have been created in the UI.

# COMMAND ----------

spark.sql(f"""
    GRANT BROWSE, USE CATALOG, USE SCHEMA, SELECT, EXECUTE, READ VOLUME
    ON CATALOG {catalog_name} TO `{catalog_name}_reader`
""")

spark.sql(f"""
    GRANT BROWSE, USE CATALOG, USE SCHEMA, SELECT, EXECUTE, READ VOLUME,
          APPLY TAG, MODIFY, CREATE FUNCTION, CREATE MATERIALIZED VIEW, CREATE MODEL, CREATE TABLE,
          READ SECRET, REFRESH
    ON CATALOG {catalog_name} TO `{catalog_name}_writer`
""")

spark.sql(f"GRANT ALL PRIVILEGES ON CATALOG {catalog_name} TO `{catalog_name}_admin`")

spark.sql(f"SHOW GRANTS ON CATALOG {catalog_name}").display()

# COMMAND ----------

# MAGIC %md ### Step 5 — Assign Users to Groups in the UI
# MAGIC Go to **Settings → Identity and Access → Groups** and assign:
# MAGIC - `{leader}` (e.g. `atintaya@utec.edu.pe`) → `{catalog_name}_admin` (e.g. `gx_mkt_clientes_admin`)
# MAGIC - each member in `{members}` (e.g. `angel.tintaya@utec.edu.pe`) → `{catalog_name}_writer` (e.g. `gx_mkt_clientes_writer`)
# MAGIC - Group `utec-de` → `{catalog_name}_reader` (e.g. `gx_mkt_clientes_reader`)

# COMMAND ----------

# MAGIC %md ### Verify — Final State

# COMMAND ----------

spark.sql(f"SHOW SCHEMAS IN {catalog_name}").display()
spark.sql(f"SHOW GRANTS ON CATALOG {catalog_name}").display()

# COMMAND ----------

# MAGIC %md ### Cleanup
# MAGIC Run this cell to delete everything created in this demo and leave the environment clean.
# MAGIC After running, also delete the three groups manually in the UI:
# MAGIC `{catalog_name}_reader`, `{catalog_name}_writer`, `{catalog_name}_admin`
# MAGIC (e.g. `gx_mkt_clientes_reader`, `gx_mkt_clientes_writer`, `gx_mkt_clientes_admin`)

# COMMAND ----------

spark.sql(f"DROP CATALOG IF EXISTS {catalog_name} CASCADE")
print(f"Catalog '{catalog_name}' and all its schemas deleted.")
print(f"Remember to delete these groups in the UI:")
print(f"  - {catalog_name}_reader")
print(f"  - {catalog_name}_writer")
print(f"  - {catalog_name}_admin")