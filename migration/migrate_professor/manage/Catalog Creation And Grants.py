# Databricks notebook source
# DBTITLE 1,Create catalogs from prefixes
prefixes = [f"g10{i}" for i in range(1, 7)] + [f"g20{i}" for i in range(1, 7)]
results = []

for prefix in prefixes:
    catalog_name = f"{prefix}_catalog"
    try:
        spark.sql(f"CREATE CATALOG IF NOT EXISTS `{catalog_name}`")
        results.append((prefix, catalog_name, "success", None))
    except Exception as e:
        results.append((prefix, catalog_name, "error", str(e)))