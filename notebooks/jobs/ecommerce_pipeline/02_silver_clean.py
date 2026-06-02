# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # Task 02 — Silver Cleaning
# MAGIC
# MAGIC **Purpose**: Read from Bronze, validate data quality, clean, enrich, and write to Silver.
# MAGIC
# MAGIC **Key concepts demonstrated**:
# MAGIC - Inline **data quality validation** with explicit pass/fail flags
# MAGIC - **Derived columns** computed at the Silver layer (`total_amount`)
# MAGIC - **Lineage** — Silver records carry the `_source_batch_id` from Bronze
# MAGIC - **Idempotent MERGE** on `order_id`
# MAGIC
# MAGIC > **Simplified for learning**: Production pipelines often use dedicated DQ frameworks
# MAGIC > like Great Expectations, Soda, or dbt tests. The logic here shows the same principles
# MAGIC > without requiring additional dependencies.

# COMMAND ----------

dbutils.widgets.text("catalog",  "my_catalog", "Unity Catalog name")
dbutils.widgets.text("run_date", "", "Run Date (YYYY-MM-DD, blank = today)")

# COMMAND ----------

import json
import logging
from datetime import datetime

from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

run_date = dbutils.widgets.get("run_date") or datetime.now().strftime("%Y-%m-%d")
CATALOG  = dbutils.widgets.get("catalog")
SCHEMA   = "ecommerce_de_class"

BRONZE_TABLE = f"{CATALOG}.{SCHEMA}.bronze_orders"
SILVER_TABLE = f"{CATALOG}.{SCHEMA}.silver_orders"

log.info(f"Starting silver cleaning | run_date={run_date} | catalog={CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Read from Bronze

# COMMAND ----------

bronze_df    = spark.table(BRONZE_TABLE).filter(F.col("_run_date") == run_date)
bronze_count = bronze_df.count()
log.info(f"Read {bronze_count} records from bronze for {run_date}")

# Exit gracefully if there is nothing to process — not an error
if bronze_count == 0:
    msg = f"No bronze records found for {run_date}. Skipping."
    log.warning(msg)
    dbutils.notebook.exit(json.dumps({"status": "skipped", "reason": msg}))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Validation
# MAGIC
# MAGIC **Teaching point — Flag, don't silently drop**:
# MAGIC
# MAGIC We add boolean validation columns instead of immediately filtering bad rows.
# MAGIC This lets us *count and log* how many records failed each rule before discarding them —
# MAGIC a silent `filter()` hides problems that may indicate upstream bugs.

# COMMAND ----------

validated_df = (
    bronze_df
    .withColumn("_qty_ok",   F.col("quantity").between(1, 100))
    .withColumn("_price_ok", F.col("unit_price") > 0)
    .withColumn("_id_ok",    F.col("order_id").isNotNull())
)

# Count and log failures per rule — useful for monitoring trends over time
for rule, col in [("quantity_range", "_qty_ok"), ("positive_price", "_price_ok"), ("non_null_id", "_id_ok")]:
    failed = validated_df.filter(~F.col(col)).count()
    log.info(f"DQ rule '{rule}': {failed} failures / {bronze_count} records")

invalid_count = validated_df.filter(
    ~F.col("_qty_ok") | ~F.col("_price_ok") | ~F.col("_id_ok")
).count()

log.info(f"Total invalid records: {invalid_count} ({invalid_count/bronze_count:.1%})")

# Keep only valid records — invalid ones are logged above and visible in bronze for audit
clean_df = validated_df.filter(
    F.col("_qty_ok") & F.col("_price_ok") & F.col("_id_ok")
).drop("_qty_ok", "_price_ok", "_id_ok")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Transform and Enrich
# MAGIC
# MAGIC `total_amount` is derived here — not stored in Bronze — because Silver is where
# MAGIC business rules are applied. If the formula changes, we reprocess Silver, not Bronze.

# COMMAND ----------

silver_df = (
    clean_df
    .withColumn("total_amount",    F.round(F.col("quantity") * F.col("unit_price"), 2))
    .withColumn("_processed_at",   F.current_timestamp())
    .withColumn("_source_batch_id", F.col("_batch_id"))   # lineage: which bronze batch
    .withColumn("_run_date",       F.to_date(F.lit(run_date)))
    .drop("_ingested_at", "_batch_id")                    # bronze-only audit columns
)

display(silver_df.orderBy("order_timestamp").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Idempotent Write to Silver

# COMMAND ----------

silver_df.createOrReplaceTempView("clean_orders")

spark.sql(f"""
  MERGE INTO {SILVER_TABLE} AS target
  USING clean_orders AS source
  ON target.order_id = source.order_id
  WHEN MATCHED THEN UPDATE SET *
  WHEN NOT MATCHED THEN INSERT *
""")

silver_count = (
    spark.table(SILVER_TABLE)
    .filter(F.col("_run_date") == run_date)
    .count()
)
pass_rate = silver_count / bronze_count
log.info(f"Silver updated | rows={silver_count} | pass_rate={pass_rate:.1%}")

# COMMAND ----------

metrics = {
    "task":            "silver_clean",
    "run_date":        run_date,
    "bronze_records":  bronze_count,
    "invalid_records": invalid_count,
    "silver_records":  silver_count,
    "pass_rate_pct":   round(pass_rate * 100, 1),
    "status":          "success",
}
log.info(f"Task metrics: {json.dumps(metrics)}")
print(f"\nSilver cleaning complete — pass rate: {pass_rate:.1%} ({silver_count}/{bronze_count})")
dbutils.notebook.exit(json.dumps(metrics))
