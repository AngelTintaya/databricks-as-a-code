# Databricks notebook source
import requests
import json

# COMMAND ----------

# Securely get the token
token = dbutils.secrets.get(scope="de-scope", key="de-secret-key")

# Use the token in your API call
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Example: List clusters
response = requests.get(
    "https://adb-1703116329100891.11.azuredatabricks.net/api/2.0/clusters/list",
    headers=headers
)

# COMMAND ----------

print(response.status_code)
print(response.json())