# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # Task 00 — Pipeline Setup
# MAGIC
# MAGIC **Purpose**: Create the database and Delta tables used by the pipeline.
# MAGIC
# MAGIC **Key teaching point — Idempotency**:
# MAGIC Every statement uses `IF NOT EXISTS`. Running this notebook 10 times produces
# MAGIC the same result as running it once. This is the foundation of reliable pipelines.
# MAGIC
# MAGIC > **Simplified for learning**: In production, schema changes (e.g. adding a column)
# MAGIC > are managed by migration tools like dbt, Liquibase, or a dedicated CI/CD process —
# MAGIC > not by dropping and recreating tables.

# COMMAND ----------

import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

dbutils.widgets.text("catalog", "my_catalog", "Unity Catalog name")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration
# MAGIC
# MAGIC Centralising config in one place means a single change switches the entire pipeline
# MAGIC between environments (dev → staging → prod).

# COMMAND ----------

CATALOG      = dbutils.widgets.get("catalog")
SCHEMA       = "ecommerce_de_class"
BRONZE_TABLE = f"{CATALOG}.{SCHEMA}.bronze_orders"
SILVER_TABLE = f"{CATALOG}.{SCHEMA}.silver_orders"
GOLD_TABLE   = f"{CATALOG}.{SCHEMA}.gold_daily_revenue"

log.info(f"Setting up {CATALOG}.{SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Database

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
log.info(f"Schema '{CATALOG}.{SCHEMA}' ready.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Bronze Table — Raw Orders
# MAGIC
# MAGIC Bronze = raw data, as close to the source as possible.
# MAGIC We add **audit columns** (prefixed `_`) to answer:
# MAGIC *"When did this record arrive, and from which batch?"*
# MAGIC These columns are critical for debugging and lineage tracking.

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {BRONZE_TABLE} (
    order_id          STRING    NOT NULL  COMMENT 'Unique order identifier',
    customer_id       STRING              COMMENT 'Customer identifier',
    product_id        STRING              COMMENT 'Product identifier',
    product_category  STRING              COMMENT 'Product category',
    quantity          INT                 COMMENT 'Units ordered',
    unit_price        DOUBLE              COMMENT 'Price per unit in USD',
    order_status      STRING              COMMENT 'pending | confirmed | shipped | cancelled',
    order_timestamp   TIMESTAMP           COMMENT 'When the order was placed',
    _ingested_at      TIMESTAMP           COMMENT 'When this record was written to bronze',
    _batch_id         STRING              COMMENT 'Unique ID for the ingestion batch',
    _run_date         DATE                COMMENT 'Partition key — the pipeline run date'
  )
  USING DELTA
  PARTITIONED BY (_run_date)
  COMMENT 'Bronze layer: raw e-commerce orders, append-or-merge only'
""")
log.info(f"Table '{BRONZE_TABLE}' ready.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver Table — Cleaned Orders
# MAGIC
# MAGIC Silver = validated, cleaned, and enriched.
# MAGIC We derive `total_amount` here instead of storing it in bronze, because
# MAGIC Silver is where business rules are applied.

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {SILVER_TABLE} (
    order_id          STRING    NOT NULL  COMMENT 'Unique order identifier',
    customer_id       STRING,
    product_id        STRING,
    product_category  STRING,
    quantity          INT,
    unit_price        DOUBLE,
    total_amount      DOUBLE              COMMENT 'Derived: quantity * unit_price',
    order_status      STRING,
    order_timestamp   TIMESTAMP,
    _processed_at     TIMESTAMP           COMMENT 'When this record was written to silver',
    _source_batch_id  STRING              COMMENT 'Lineage: the bronze batch this came from',
    _run_date         DATE
  )
  USING DELTA
  PARTITIONED BY (_run_date)
  COMMENT 'Silver layer: validated and enriched orders'
""")
log.info(f"Table '{SILVER_TABLE}' ready.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Table — Daily Revenue Aggregates
# MAGIC
# MAGIC Gold = business-ready. These are the tables analysts, dashboards, and reports consume.
# MAGIC Aggregated at the `(report_date, product_category)` grain.

# COMMAND ----------

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {GOLD_TABLE} (
    report_date       DATE      NOT NULL  COMMENT 'The business date for this aggregate',
    product_category  STRING    NOT NULL  COMMENT 'Product category',
    total_orders      LONG                COMMENT 'Count of non-cancelled orders',
    total_revenue     DOUBLE              COMMENT 'Sum of total_amount for the day',
    avg_order_value   DOUBLE              COMMENT 'Average order value for the day',
    _computed_at      TIMESTAMP           COMMENT 'When this aggregate was last computed'
  )
  USING DELTA
  COMMENT 'Gold layer: daily revenue by product category'
""")
log.info(f"Table '{GOLD_TABLE}' ready.")

# COMMAND ----------

log.info("Setup complete.")
print(f"""
Setup complete!
  Catalog  : {CATALOG}
  Schema   : {SCHEMA}
  Tables   : bronze_orders, silver_orders, gold_daily_revenue

Run `DESCRIBE HISTORY {BRONZE_TABLE}` after a few pipeline runs to see Delta versioning in action.
""")
