# Databricks notebook source
# MAGIC %md
# MAGIC # Creación de Schemas

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP SCHEMA IF EXISTS g0_ops_productos.bronze CASCADE;
# MAGIC DROP SCHEMA IF EXISTS g0_ops_productos.silver CASCADE;
# MAGIC DROP SCHEMA IF EXISTS g0_ops_productos.gold CASCADE;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE DATABASE g0_ops_productos.bronze;
# MAGIC CREATE DATABASE g0_ops_productos.silver;
# MAGIC CREATE DATABASE g0_ops_productos.gold;