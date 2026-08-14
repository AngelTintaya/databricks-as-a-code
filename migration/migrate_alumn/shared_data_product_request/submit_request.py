# Databricks notebook source
# MAGIC %run ./utils

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Product Request
# MAGIC 1. Fill in all variables in the cell below.
# MAGIC 2. Click **Run All**.
# MAGIC 3. Fix any validation errors and re-run until successful.

# COMMAND ----------

group   = "gx05"                  # g101–g106 or g201–g206
leader  = "atintaya@utec.edu.pe"                     # e.g. juan.perez@utec.edu.pe
members = "atintaya@utec.edu.pe, winston.flores@utec.edu.pe, piero.palacios@utec.edu.pe, nicolas.quiroz@utec.edu.pe, diego.perez.b@utec.edu.pe"   # Comma-separated; do not include the leader

# One tuple per data product: (domain_code, domain_name, dp_name)
# domain_code : exactly 3 lowercase letters        e.g. "cmc"
# domain_name : max 20 chars, meaning of the code  e.g. "comercial"
# dp_name     : max 20 chars, data product name    e.g. "ventas"
data_products = [
    ("cmc", "comercial", "ventas"),
    ("ops", "operaciones", "productos"),
    ("mkt", "marketing", "clientes"),
]

# COMMAND ----------

submit_dataproduct_request(group, leader, members, data_products)