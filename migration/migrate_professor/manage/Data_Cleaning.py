# Databricks notebook source
df = spark.sql("SHOW CATALOGS")

# COMMAND ----------

df = spark.sql("SHOW CATALOGS")
suffixes = ['g1_', 'g2_', 'g3_', 'g4_', 'g5_', 'g6_', 'g7_', 'g8_', 'gx_', 'g01_', 'g10_', 'g11_', 'ga_']
filtered_catalogs = df.filter(
    df.catalog.rlike("^(" + "|".join(suffixes) + ")")
)

# COMMAND ----------

schemas = ['bronze', 'silver', 'gold', 'default', 'support']

# COMMAND ----------

catalog_list = [row.catalog for row in filtered_catalogs.collect()]

for catalog in catalog_list:
    for schema in schemas:
        spark.sql(
            f"DROP SCHEMA IF EXISTS {catalog}.{schema} CASCADE"
        )

# COMMAND ----------

catalog_list = [row.catalog for row in filtered_catalogs.collect()]
print(catalog_list)
for catalog in catalog_list:
    spark.sql(
        f"DROP CATALOG IF EXISTS {catalog}"
    )

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP SCHEMA IF EXISTS gx_mkt_clientes.support CASCADE