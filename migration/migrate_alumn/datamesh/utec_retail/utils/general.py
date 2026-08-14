# Databricks notebook source
def greet(name):
    return f"Hello, {name}!"

# COMMAND ----------

def widget_exists(widget_name):
    try:
        dbutils.widgets.get(widget_name)
        return True
    except:
        return False