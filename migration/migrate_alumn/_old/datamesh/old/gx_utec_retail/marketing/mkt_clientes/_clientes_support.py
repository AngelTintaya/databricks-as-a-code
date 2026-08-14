# Databricks notebook source
# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS g0_mkt_clientes.support.errores_validacion;

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS g0_mkt_clientes.support.cuarentena_raw_clientes

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE g0_mkt_clientes.support.errores_validacion
# MAGIC (
# MAGIC   valid_id BIGINT GENERATED ALWAYS AS IDENTITY,
# MAGIC   process STRING,
# MAGIC   total_errores BIGINT,
# MAGIC   tipo_error STRING,
# MAGIC   created_at DATE
# MAGIC )
# MAGIC ;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE g0_mkt_clientes.support.cuarentena_raw_clientes
# MAGIC (
# MAGIC   cliente_id STRING,
# MAGIC   nombre STRING,
# MAGIC   email STRING,
# MAGIC   fecha_nacimiento STRING,
# MAGIC   genero STRING,
# MAGIC   ubicacion STRING,
# MAGIC   fecha STRING,
# MAGIC   inserted_at TIMESTAMP
# MAGIC )
# MAGIC ;