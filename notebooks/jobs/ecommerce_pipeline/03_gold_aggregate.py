# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # Task 03 — Gold Aggregation
# MAGIC
# MAGIC **Purpose**: Aggregate Silver into daily business metrics and write to Gold.
# MAGIC
# MAGIC **Key concepts demonstrated**:
# MAGIC - **Business-level aggregates** — the tables analysts and dashboards consume
# MAGIC - **Idempotent MERGE** on a composite key `(report_date, product_category)`
# MAGIC - **Delta time travel** — every run is a new Delta version; you can query any past state
# MAGIC - **Execution metrics** — revenue summary logged for monitoring
# MAGIC
# MAGIC > **Simplified for learning**: In production, Gold tables often power BI tools
# MAGIC > (Tableau, Power BI) or are exposed as Databricks SQL queries. The aggregation
# MAGIC > logic here would typically live in dbt models or a SQL warehouse.

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

SILVER_TABLE = f"{CATALOG}.{SCHEMA}.silver_orders"
GOLD_TABLE   = f"{CATALOG}.{SCHEMA}.gold_daily_revenue"

log.info(f"Starting gold aggregation | run_date={run_date} | catalog={CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Aggregate from Silver
# MAGIC
# MAGIC We exclude `cancelled` orders from revenue — a business rule that belongs at the
# MAGIC Gold layer because different consumers may have different rules.
# MAGIC Bronze and Silver retain the cancelled records for completeness.

# COMMAND ----------

silver_df = spark.table(SILVER_TABLE).filter(
    (F.col("_run_date") == run_date) & (F.col("order_status") != "cancelled")
)

gold_df = (
    silver_df
    .groupBy("product_category")
    .agg(
        F.count("order_id").alias("total_orders"),
        F.round(F.sum("total_amount"),  2).alias("total_revenue"),
        F.round(F.avg("total_amount"),  2).alias("avg_order_value"),
    )
    .withColumn("report_date",  F.to_date(F.lit(run_date)))
    .withColumn("_computed_at", F.current_timestamp())
)

display(gold_df.orderBy(F.desc("total_revenue")))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Idempotent Write to Gold
# MAGIC
# MAGIC **Teaching point — Composite MERGE key**:
# MAGIC
# MAGIC The key is `(report_date, product_category)` — one row per day per category.
# MAGIC Re-running for the same date *replaces* the aggregate instead of appending a second row.
# MAGIC
# MAGIC After this runs, try: `DESCRIBE HISTORY {GOLD_TABLE}`
# MAGIC to see Delta versioning in action. You can query any prior version with
# MAGIC `SELECT * FROM {GOLD_TABLE} VERSION AS OF 1`.

# COMMAND ----------

gold_df.createOrReplaceTempView("daily_revenue")

spark.sql(f"""
  MERGE INTO {GOLD_TABLE} AS target
  USING daily_revenue AS source
  ON  target.report_date      = source.report_date
  AND target.product_category = source.product_category
  WHEN MATCHED THEN UPDATE SET *
  WHEN NOT MATCHED THEN INSERT *
""")

total_revenue = gold_df.agg(F.sum("total_revenue")).collect()[0][0] or 0.0
total_orders  = gold_df.agg(F.sum("total_orders")).collect()[0][0]  or 0

log.info(f"Gold updated | total_revenue=${total_revenue:,.2f} | total_orders={total_orders}")

# COMMAND ----------

metrics = {
    "task":           "gold_aggregate",
    "run_date":       run_date,
    "categories":     gold_df.count(),
    "total_orders":   int(total_orders),
    "total_revenue":  round(total_revenue, 2),
    "status":         "success",
}
log.info(f"Task metrics: {json.dumps(metrics)}")
print(f"\nGold aggregation complete — ${total_revenue:,.2f} revenue across {metrics['categories']} categories")
dbutils.notebook.exit(json.dumps(metrics))
