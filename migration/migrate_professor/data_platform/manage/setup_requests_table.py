# Databricks notebook source
# MAGIC %md
# MAGIC ## Setup — Requests Table
# MAGIC Run this notebook **once** as the catalog owner to create the schema, table, and grants.
# MAGIC Must be run interactively by `atintaya@utec.edu.pe` (catalog owner of `data_platform`).

# COMMAND ----------

spark.sql("CREATE SCHEMA IF NOT EXISTS data_platform.admin")
print("Schema data_platform.admin ready")

# COMMAND ----------

spark.sql("""
    CREATE TABLE IF NOT EXISTS data_platform.admin.dataproduct_requests (
        group        STRING    NOT NULL,
        leader       STRING    NOT NULL,
        members      STRING    NOT NULL,
        domain_code  STRING    NOT NULL,
        domain_name  STRING    NOT NULL,
        dp_name      STRING    NOT NULL,
        status       STRING    NOT NULL DEFAULT 'pending',
        error        STRING,
        submitted_at TIMESTAMP NOT NULL,
        processed_at TIMESTAMP
    )
    USING DELTA
    TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported')
    COMMENT 'Student data product requests. One row per data product.'
""")
print("Table data_platform.admin.dataproduct_requests ready")

# COMMAND ----------

# utec-de needs USE CATALOG to enter the catalog at all
spark.sql("GRANT USE CATALOG ON CATALOG data_platform TO `utec-de`")

# utec-de can access the schema
spark.sql("GRANT USE SCHEMA ON SCHEMA data_platform.admin TO `utec-de`")

# utec-de can read status, submit new requests, and update pending ones
spark.sql("GRANT SELECT, MODIFY ON TABLE data_platform.admin.dataproduct_requests TO `utec-de`")

print("Grants applied to utec-de")
