# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # Task 01 — Bronze Ingestion
# MAGIC
# MAGIC **Purpose**: Generate synthetic order data and write it to the Bronze Delta table.
# MAGIC
# MAGIC **Key concepts demonstrated**:
# MAGIC - Notebook parameters via **widgets** — the job passes `run_date` at runtime
# MAGIC - **Deterministic data generation** — same `run_date` always produces the same records
# MAGIC - **Idempotent writes** via Delta MERGE — retrying the job never creates duplicates
# MAGIC - **Structured logging** — JSON metrics emitted at the end for observability
# MAGIC
# MAGIC > **Simplified for learning**: In production, data arrives from Kafka, S3, an API,
# MAGIC > or CDC streams. We generate it here so the demo works without external dependencies.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Parameters
# MAGIC
# MAGIC Widgets let you run this notebook interactively with custom values,
# MAGIC or let the Databricks Job pass values automatically at runtime.

# COMMAND ----------

dbutils.widgets.text("catalog",    "my_catalog", "Unity Catalog name")
dbutils.widgets.text("run_date",   "", "Run Date (YYYY-MM-DD, blank = today)")
dbutils.widgets.text("batch_size", "200", "Number of orders to generate")

# COMMAND ----------

import json
import logging
import random
import uuid
from datetime import datetime, timedelta

from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Default to today when run interactively without a date
run_date   = dbutils.widgets.get("run_date") or datetime.now().strftime("%Y-%m-%d")
batch_size = int(dbutils.widgets.get("batch_size"))
CATALOG    = dbutils.widgets.get("catalog")
SCHEMA     = "ecommerce_de_class"

BRONZE_TABLE = f"{CATALOG}.{SCHEMA}.bronze_orders"

# Unique batch ID per run — uuid4 works on all cluster types including shared/Unity Catalog
BATCH_ID = f"bronze_{run_date.replace('-', '')}_{str(uuid.uuid4())[:8]}"

log.info(f"Starting bronze ingestion | run_date={run_date} | catalog={CATALOG} | batch_size={batch_size} | batch_id={BATCH_ID}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Synthetic Data
# MAGIC
# MAGIC **Teaching point — Idempotency via seeded randomness**:
# MAGIC
# MAGIC Using `run_date` as the random seed means this function always produces
# MAGIC **the same orders for the same date**, no matter how many times it's called.
# MAGIC
# MAGIC Why does this matter? If the job fails at 80% completion and retries,
# MAGIC you want to re-process the *same* data — not different data.
# MAGIC Non-deterministic generation would create silent data corruption on retry.

# COMMAND ----------

CATEGORIES = ["Electronics", "Clothing", "Books", "Sports", "Home"]
STATUSES   = ["confirmed", "shipped", "pending", "cancelled"]

def generate_orders(run_date: str, n: int) -> list[dict]:
    """
    Deterministic order generation — same run_date always returns identical records.
    In production this would be replaced by a read from a source system.
    """
    rng     = random.Random(int(run_date.replace("-", "")))  # seed = date as int
    base_ts = datetime.strptime(run_date, "%Y-%m-%d")
    return [
        {
            "order_id":         f"ORD-{run_date.replace('-', '')}-{i:05d}",
            "customer_id":      f"CUST-{rng.randint(1000, 9999)}",
            "product_id":       f"PROD-{rng.randint(100, 999)}",
            "product_category": rng.choice(CATEGORIES),
            "quantity":         rng.randint(1, 10),
            "unit_price":       round(rng.uniform(5.0, 500.0), 2),
            "order_status":     rng.choices(STATUSES, weights=[50, 30, 15, 5])[0],
            "order_timestamp":  base_ts + timedelta(seconds=rng.randint(0, 86399)),
        }
        for i in range(n)
    ]

raw_orders = generate_orders(run_date, batch_size)
log.info(f"Generated {len(raw_orders)} orders")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Add Audit Columns
# MAGIC
# MAGIC Audit columns (prefixed `_`) answer: *"When did this data arrive, and from which batch?"*
# MAGIC These are never from the source — we add them ourselves to support lineage and debugging.

# COMMAND ----------

df = (
    spark.createDataFrame(raw_orders)
    .withColumn("_ingested_at", F.current_timestamp())
    .withColumn("_batch_id",    F.lit(BATCH_ID))
    .withColumn("_run_date",    F.to_date(F.lit(run_date)))
)

display(df.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Idempotent Write — Delta MERGE
# MAGIC
# MAGIC **Teaching point**: `INSERT OVERWRITE` would work for a full partition replacement,
# MAGIC but MERGE gives row-level idempotency: if `order_id` already exists, we *update*
# MAGIC it instead of creating a duplicate. Run this cell 5 times — same result every time.

# COMMAND ----------

df.createOrReplaceTempView("new_orders")

spark.sql(f"""
  MERGE INTO {BRONZE_TABLE} AS target
  USING new_orders AS source
  ON target.order_id = source.order_id
  WHEN MATCHED THEN
    UPDATE SET *
  WHEN NOT MATCHED THEN
    INSERT *
""")

rows_in_bronze = (
    spark.table(BRONZE_TABLE)
    .filter(F.col("_run_date") == run_date)
    .count()
)
log.info(f"MERGE complete | rows in bronze for {run_date}: {rows_in_bronze}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Task Output — Structured Metrics
# MAGIC
# MAGIC `dbutils.notebook.exit()` passes a JSON payload to the job orchestrator.
# MAGIC Downstream tasks can read this via `{{tasks.bronze_ingest.values.batch_id}}`.
# MAGIC It also appears in the job run UI — useful for at-a-glance observability.

# COMMAND ----------

metrics = {
    "task":              "bronze_ingest",
    "run_date":          run_date,
    "batch_id":          BATCH_ID,
    "records_generated": batch_size,
    "records_in_bronze": rows_in_bronze,
    "status":            "success",
}
log.info(f"Task metrics: {json.dumps(metrics)}")
print(f"\nBronze ingestion complete — {rows_in_bronze} records for {run_date}")
dbutils.notebook.exit(json.dumps(metrics))
