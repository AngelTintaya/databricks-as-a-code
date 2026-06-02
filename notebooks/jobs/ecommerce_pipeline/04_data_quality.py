# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # Task 04 — Data Quality Gate
# MAGIC
# MAGIC **Purpose**: Run end-to-end quality checks across all three layers.
# MAGIC Raise an exception on critical failures to trigger retries and failure alerts.
# MAGIC
# MAGIC **Key concepts demonstrated**:
# MAGIC - **DQ as a pipeline stage** — not an afterthought
# MAGIC - **Critical vs. warning checks** — not all failures should stop the pipeline
# MAGIC - **Exception-driven alerting** — raising here triggers the job retry policy,
# MAGIC   and after max retries Databricks sends a failure email automatically
# MAGIC
# MAGIC > **Simplified for learning**: Production systems often use Great Expectations, Soda Core,
# MAGIC > or dbt tests for this. The check pattern here is identical — they just give you a
# MAGIC > richer reporting layer on top.

# COMMAND ----------

dbutils.widgets.text("catalog",       "my_catalog", "Unity Catalog name")
dbutils.widgets.text("run_date",      "",           "Run Date (YYYY-MM-DD, blank = today)")
dbutils.widgets.text("min_pass_rate", "0.90",       "Minimum Silver pass rate (0.0 – 1.0)")

# COMMAND ----------

import json
import logging
from datetime import datetime

from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

run_date      = dbutils.widgets.get("run_date") or datetime.now().strftime("%Y-%m-%d")
min_pass_rate = float(dbutils.widgets.get("min_pass_rate"))
CATALOG       = dbutils.widgets.get("catalog")
SCHEMA        = "ecommerce_de_class"

BRONZE_TABLE = f"{CATALOG}.{SCHEMA}.bronze_orders"
SILVER_TABLE = f"{CATALOG}.{SCHEMA}.silver_orders"
GOLD_TABLE   = f"{CATALOG}.{SCHEMA}.gold_daily_revenue"

log.info(f"Starting DQ gate | run_date={run_date} | catalog={CATALOG} | min_pass_rate={min_pass_rate:.0%}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Quality Checks
# MAGIC
# MAGIC Each check records its result. `critical=True` means a failure will stop the pipeline.
# MAGIC Warning-level failures are logged and visible in the job output, but don't stop execution.

# COMMAND ----------

checks = []

def check(name: str, passed: bool, detail: str, critical: bool = False):
    status = "PASS" if passed else ("FAIL_CRITICAL" if critical else "FAIL_WARNING")
    checks.append({"check": name, "status": status, "detail": detail, "critical": critical})
    level = logging.ERROR if (not passed and critical) else logging.WARNING if not passed else logging.INFO
    log.log(level, f"[DQ] {status:15s} | {name:30s} | {detail}")

# ── Check 1: Bronze has data for this date ────────────────────────────────────
bronze_count = spark.table(BRONZE_TABLE).filter(F.col("_run_date") == run_date).count()
check("bronze_has_data", bronze_count > 0, f"count={bronze_count}", critical=True)

# ── Check 2: Silver pass rate meets the configured threshold ─────────────────
silver_count = spark.table(SILVER_TABLE).filter(F.col("_run_date") == run_date).count()
pass_rate    = silver_count / bronze_count if bronze_count > 0 else 0.0
check(
    "silver_pass_rate",
    pass_rate >= min_pass_rate,
    f"{pass_rate:.1%} ({silver_count}/{bronze_count}) — minimum: {min_pass_rate:.0%}",
    critical=True,
)

# ── Check 3: No null order IDs in Silver ─────────────────────────────────────
null_ids = (
    spark.table(SILVER_TABLE)
    .filter((F.col("_run_date") == run_date) & F.col("order_id").isNull())
    .count()
)
check("no_null_order_ids", null_ids == 0, f"null_ids={null_ids}", critical=True)

# ── Check 4: All Silver amounts are positive ──────────────────────────────────
bad_amounts = (
    spark.table(SILVER_TABLE)
    .filter((F.col("_run_date") == run_date) & (F.col("total_amount") <= 0))
    .count()
)
check("positive_total_amount", bad_amounts == 0, f"non_positive={bad_amounts}", critical=True)

# ── Check 5: Gold has rows for this date (pipeline ran end-to-end) ────────────
gold_rows = spark.table(GOLD_TABLE).filter(F.col("report_date") == run_date).count()
check("gold_has_data", gold_rows > 0, f"gold_rows={gold_rows}", critical=True)

# ── Check 6: Gold revenue is reasonable (warning only) ───────────────────────
total_revenue = (
    spark.table(GOLD_TABLE)
    .filter(F.col("report_date") == run_date)
    .agg(F.sum("total_revenue"))
    .collect()[0][0] or 0.0
)
check("gold_revenue_positive", total_revenue > 0, f"total_revenue=${total_revenue:,.2f}", critical=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Results

# COMMAND ----------

results_df = spark.createDataFrame(checks)
display(results_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gate Decision
# MAGIC
# MAGIC **Teaching point — Exception = retry trigger + alert**:
# MAGIC
# MAGIC When this task raises an exception, Databricks retries it up to `max_retries` times.
# MAGIC After all retries are exhausted, it sends the failure email configured in the job.
# MAGIC This is the mechanism that connects code failures to human notification — no extra
# MAGIC infrastructure needed.

# COMMAND ----------

critical_failures = [c for c in checks if c["critical"] and "FAIL" in c["status"]]

if critical_failures:
    failed_names = [c["check"] for c in critical_failures]
    msg = f"CRITICAL DQ FAILURES for {run_date}: {failed_names}"
    log.error(msg)
    raise Exception(msg)  # triggers retry policy → then failure email alert

log.info(f"All {len(checks)} DQ checks passed for {run_date}.")
print(f"\nDQ gate passed — {len(checks)} checks, 0 critical failures")
dbutils.notebook.exit(json.dumps({"status": "passed", "run_date": run_date, "checks": checks}))
