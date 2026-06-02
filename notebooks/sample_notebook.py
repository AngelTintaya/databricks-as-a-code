# Databricks notebook source

# COMMAND ----------

# Sample Databricks Notebook
# This notebook demonstrates basic Databricks operations

# COMMAND ----------

# Display Python version
import sys
print(f"Python version: {sys.version}")

# COMMAND ----------

# Create a simple DataFrame
data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
columns = ["Name", "Age"]

df = spark.createDataFrame(data, columns)
df.display()

# COMMAND ----------

# Show Databricks cluster information
dbutils.notebook.getContext().tags().getOrElse('cluster_id', 'N/A')
