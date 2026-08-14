# Databricks notebook source
# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS g0_catalog.default.bronze_sql_input;
# MAGIC DROP TABLE IF EXISTS g0_catalog.default.silver_sql_transform;
# MAGIC DROP TABLE IF EXISTS g0_catalog.default.gold_sql_summary;