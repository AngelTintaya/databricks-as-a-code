# Databricks notebook source
import re

# COMMAND ----------

token = dbutils.secrets.get(scope="de-scope", key="de-secret-key")
account_id = '25ecde06-8cd3-4377-863b-acf4d84b39d8'
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# COMMAND ----------

admin = 'atintaya@utec.edu.pe'

# COMMAND ----------

workspace = 'adb-1703116329100891.11'
workspace_url = f'https://{workspace}.azuredatabricks.net'
warehouse_id = '8ba2a6f5ddb13574'

# COMMAND ----------

workspace_pattern = re.compile(r'adb-(\d+)\.\d')
workspace_id = workspace_pattern.findall(workspace)[0]

# COMMAND ----------

endpoints = {
    'users_endpoint': f'{workspace_url}/api/2.0/preview/scim/v2/Users',
    'groups_endpoint': f'{workspace_url}/api/2.0/preview/scim/v2/Groups',
    'rule_sets_endpoint': f'{workspace_url}/api/2.0/preview/accounts/access-control/rule-sets',
    'genie_endpoint': f'{workspace_url}/api/2.0/data-rooms',
    'folders_endpoint': f'{workspace_url}/api/2.0/folders',
    'access_policies_endpoint': f'{workspace_url}/api/2.0/accesspolicies'
}

# COMMAND ----------

schema_descriptions = {
    'bronze': 'Raw data schema',
    'silver': 'Cleaned data schema',
    'gold': 'Aggregated data schema'
}

# COMMAND ----------

privileges = {
    'reader': ['BROWSE', 'USE CATALOG', 'USE SCHEMA', 'SELECT', 'EXECUTE', 'READ VOLUME'],
    'writer': ['BROWSE', 'USE CATALOG', 'USE SCHEMA', 'SELECT', 'EXECUTE', 'READ VOLUME',
               'APPLY TAG', 'MODIFY', 'CREATE FUNCTION', 'CREATE MATERIALIED VIEW', 'CREATE MODEL', 'CREATE TABLE'],
    'admin': ['ALL PRIVILEGES'],
    # 'genie_reader': ['USE SCHEMA'],
    # 'genie_admin': ['USE SCHEMA']
}

# COMMAND ----------

genie_permissions = {
    'genie_reader': ['CAN_RUN'],
    'genie_admin': ['CAN_MANAGE']
}