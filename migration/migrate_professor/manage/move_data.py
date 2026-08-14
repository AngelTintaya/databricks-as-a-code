# Databricks notebook source
dbutils.fs.mv(
    "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/DSAI_202501",
    "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/_old/DSAI_202501",
    recurse=True
    )

# COMMAND ----------

# DBTITLE 1,Move folder recursively
folders = ['g4']

archive_root = "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow/_old/DSAI_202502"
source_root = "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow"


def move_tree(src, dst):
    dbutils.fs.mkdirs(dst)
    for item in dbutils.fs.ls(src):
        if item.isDir():
            move_tree(item.path, f"{dst.rstrip('/')}/{item.name.rstrip('/')}" )
        else:
            dbutils.fs.mv(item.path, f"{dst.rstrip('/')}/{item.name}")


for folder in folders:
    move_tree(
        f"{source_root}/{folder}",
        f"{archive_root}/{folder}"
    )