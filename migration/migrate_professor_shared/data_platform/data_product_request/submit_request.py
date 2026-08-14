# Databricks notebook source
# MAGIC %run ./utils

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Product Request
# MAGIC 1. Fill in all variables in the cell below.
# MAGIC 2. Click **Run All**.
# MAGIC 3. Fix any validation errors and re-run until successful.

# COMMAND ----------

group   = "g204"                  # g101–g106 or g201–g206
leader  = "christian.cordova@utec.edu.pe"                     # e.g. juan.perez@utec.edu.pe
members = "yesseliz.choque@utec.edu.pe,kevin.zevallos.l@utec.edu.pe,meliza.sosa@utec.edu.pe"   # Comma-separated; do not include the leader

# One tuple per data product: (domain_code, domain_name, dp_name)
# domain_code : exactly 3 lowercase letters        e.g. "cmc"
# domain_name : max 20 chars, meaning of the code  e.g. "comercial"
# dp_name     : max 20 chars, data product name    e.g. "ventas"
data_products = [
    ("ops", "operaciones", "entregas"),  # ok
    ("cmc", "comercial", "demanda_zonal"),
    ("mkt", "marketing", "clientes_g4"),  # se reemplaza
]

# COMMAND ----------

submit_dataproduct_request(group, leader, members, data_products)

# COMMAND ----------

# Corre esto para verificar si el catálogo automatizado ya aparece en tu entorno
display(spark.sql("SHOW CATALOGS"))

# COMMAND ----------

catalog_mkt = "g204_mkt_clientes_g4"
catalog_ops = "g204_ops_entregas"
catalog_cmc = "g204_cmc_demanda_zonal"

# --- Catálogo: MKT Clientes ---
spark.sql(f"CREATE DATABASE IF NOT EXISTS {catalog_mkt}.bronze")
spark.sql(f"CREATE DATABASE IF NOT EXISTS {catalog_mkt}.silver")
spark.sql(f"CREATE DATABASE IF NOT EXISTS {catalog_mkt}.gold")

# --- Catálogo: OPS Entregas ---
spark.sql(f"CREATE DATABASE IF NOT EXISTS {catalog_ops}.bronze")
spark.sql(f"CREATE DATABASE IF NOT EXISTS {catalog_ops}.silver")
spark.sql(f"CREATE DATABASE IF NOT EXISTS {catalog_ops}.gold")

# --- Catálogo: CMC Demanda Zonal ---
spark.sql(f"CREATE DATABASE IF NOT EXISTS {catalog_cmc}.bronze")
spark.sql(f"CREATE DATABASE IF NOT EXISTS {catalog_cmc}.silver")
spark.sql(f"CREATE DATABASE IF NOT EXISTS {catalog_cmc}.gold")

print("¡Todos los databases (bronze, silver, gold) han sido creados con éxito!")

# COMMAND ----------

# Muestra todos los grupos registrados en el entorno de Unity Catalog
display(spark.sql("SHOW GROUPS"))