# Databricks notebook source
# MAGIC %md
# MAGIC # Test_MV

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Setup
# MAGIC DROP TABLE IF EXISTS g0_catalog.default.test_table;
# MAGIC DROP VIEW IF EXISTS g0_catalog.default.test_view;
# MAGIC DROP MATERIALIZED VIEW IF EXISTS g0_catalog.default.test_mv;
# MAGIC
# MAGIC -- Tables
# MAGIC -- ======
# MAGIC CREATE OR REPLACE TABLE g0_catalog.default.test_table AS
# MAGIC SELECT 'id_1' AS COD_ID;
# MAGIC
# MAGIC SELECT * FROM g0_catalog.default.test_table;
# MAGIC
# MAGIC -- Views
# MAGIC -- =====
# MAGIC CREATE OR REPLACE VIEW g0_catalog.default.test_view AS
# MAGIC SELECT * FROM g0_catalog.default.test_table;
# MAGIC
# MAGIC SELECT * FROM g0_catalog.default.test_view;
# MAGIC
# MAGIC -- Materialized views
# MAGIC -- ===================
# MAGIC CREATE OR REPLACE MATERIALIZED VIEW g0_catalog.default.test_mv AS
# MAGIC SELECT * FROM g0_catalog.default.test_view;
# MAGIC
# MAGIC SELECT * FROM g0_catalog.default.test_mv;
# MAGIC
# MAGIC -- USE CASE: Adding data to table
# MAGIC -- ==============================
# MAGIC INSERT INTO g0_catalog.default.test_table VALUES ('id_2');
# MAGIC
# MAGIC SELECT * FROM g0_catalog.default.test_table;
# MAGIC -- Results in View (No es necesario recrear una vista)
# MAGIC SELECT * FROM g0_catalog.default.test_view;
# MAGIC
# MAGIC -- Results in Materialized View (No es necesario recrear un MV, sólo es necesario hacer un refresh)
# MAGIC SELECT * FROM g0_catalog.default.test_mv;
# MAGIC
# MAGIC REFRESH g0_catalog.default.test_mv;
# MAGIC SELECT * FROM g0_catalog.default.test_mv;
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # Test_PII

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ga_mkt_clientes.gold.vw_clientes;

# COMMAND ----------

# MAGIC %md
# MAGIC # Test_Retail_Queries

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM g0_mkt_clientes.bronze.raw_clientes;
# MAGIC SELECT * FROM g0_mkt_clientes.gold.vw_clientes; -- C001: Juan Pérez
# MAGIC SELECT * FROM g0_mkt_clientes.gold.vw_clientes_perfil;
# MAGIC
# MAGIC SELECT * FROM g0_mkt_clientes.support.errores_validacion;
# MAGIC SELECT * FROM g0_mkt_clientes.support.cuarentena_raw_clientes;
# MAGIC
# MAGIC SELECT * FROM g0_ops_productos.bronze.raw_inventario;
# MAGIC SELECT * FROM g0_ops_productos.gold.vw_inventario;
# MAGIC SELECT * FROM g0_ops_productos.gold.vw_hm_producto_performance;
# MAGIC SELECT * FROM g0_ops_productos.gold.vw_um_producto_performance;
# MAGIC
# MAGIC SELECT * FROM g0_cmc_ventas.bronze.raw_ventas_ecommerce;
# MAGIC SELECT * FROM g0_cmc_ventas.bronze.raw_ventas_tienda;
# MAGIC SELECT * FROM g0_cmc_ventas.silver.vw_ventas;
# MAGIC SELECT * FROM g0_cmc_ventas.silver.mv_ventas;
# MAGIC SELECT * FROM g0_cmc_ventas.gold.vw_ventas;