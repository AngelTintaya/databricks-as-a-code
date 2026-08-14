# Databricks notebook source
# MAGIC %md
# MAGIC # Creación de Schemas

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP SCHEMA IF EXISTS gx00_cmc_ventas.bronze CASCADE;
# MAGIC DROP SCHEMA IF EXISTS gx00_cmc_ventas.silver CASCADE;
# MAGIC DROP SCHEMA IF EXISTS gx00_cmc_ventas.gold CASCADE;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE DATABASE gx00_cmc_ventas.bronze;
# MAGIC CREATE DATABASE gx00_cmc_ventas.silver;
# MAGIC CREATE DATABASE gx00_cmc_ventas.gold;