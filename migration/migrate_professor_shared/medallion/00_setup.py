# Databricks notebook source
my_catalog = 'g204_gmc_demanda'
my_schemas = ['bronze', 'silver', 'gold']

# COMMAND ----------

for my_schema in my_schemas:
    spark.sql(f'DROP SCHEMA IF EXISTS {my_catalog}.{my_schema} CASCADE')

# COMMAND ----------

for my_schema in my_schemas:
    spark.sql(f'CREATE DATABASE {my_catalog}.{my_schema}')