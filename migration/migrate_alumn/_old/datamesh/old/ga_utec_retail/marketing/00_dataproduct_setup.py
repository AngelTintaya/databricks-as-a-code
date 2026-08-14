# Databricks notebook source
# MAGIC %md
# MAGIC # Creación de Schemas

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP SCHEMA IF EXISTS ga_mkt_clientes.bronze CASCADE;
# MAGIC DROP SCHEMA IF EXISTS ga_mkt_clientes.silver CASCADE;
# MAGIC DROP SCHEMA IF EXISTS ga_mkt_clientes.gold CASCADE;
# MAGIC DROP SCHEMA IF EXISTS ga_mkt_clientes.support CASCADE;

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP SCHEMA IF EXISTS ga_mkt_clientes.default CASCADE;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE DATABASE g0_mkt_clientes.bronze;
# MAGIC CREATE DATABASE g0_mkt_clientes.silver;
# MAGIC CREATE DATABASE g0_mkt_clientes.gold;
# MAGIC CREATE DATABASE g0_mkt_clientes.support;