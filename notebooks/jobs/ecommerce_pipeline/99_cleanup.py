# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # Task 99 — Classroom Cleanup
# MAGIC
# MAGIC **Purpose**: Drop all tables and the database to reset between demos.
# MAGIC
# MAGIC > **This notebook is NOT part of the production job.**
# MAGIC > It exists only to make it easy to reset the classroom environment.
# MAGIC > Set the `confirm_drop` widget to `YES` to proceed — the default is `NO`
# MAGIC > to prevent accidental runs.

# COMMAND ----------

dbutils.widgets.text("catalog",      "my_catalog", "Unity Catalog name")
dbutils.widgets.dropdown("confirm_drop", "NO", ["NO", "YES"], "Drop everything? (YES to confirm)")

# COMMAND ----------

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

CATALOG = dbutils.widgets.get("catalog")
SCHEMA  = "ecommerce_de_class"

confirm = dbutils.widgets.get("confirm_drop")
if confirm != "YES":
    print("Aborted. Set 'confirm_drop' to YES to drop the schema.")
    dbutils.notebook.exit("aborted")

# COMMAND ----------

spark.sql(f"DROP SCHEMA IF EXISTS {CATALOG}.{SCHEMA} CASCADE")
log.info(f"Schema '{CATALOG}.{SCHEMA}' dropped.")
print(f"\nCleanup complete. '{CATALOG}.{SCHEMA}' and all its tables have been dropped.")
print("Re-run 00_setup to start fresh.")
