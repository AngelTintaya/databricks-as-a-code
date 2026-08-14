# Databricks notebook source
# MAGIC %sql
# MAGIC DROP SCHEMA IF EXISTS g6_catalog.bronze CASCADE;
# MAGIC DROP SCHEMA IF EXISTS g6_catalog.silver CASCADE;
# MAGIC DROP SCHEMA IF EXISTS g6_catalog.gold CASCADE;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE DATABASE g6_catalog.bronze;
# MAGIC CREATE DATABASE g6_catalog.silver;
# MAGIC CREATE DATABASE g6_catalog.gold;

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS g6_catalog.bronze.spark_sql_input;
# MAGIC DROP TABLE IF EXISTS g6_catalog.silver.spark_sql_transform;
# MAGIC DROP TABLE IF EXISTS g6_catalog.gold.spark_sql_summary;