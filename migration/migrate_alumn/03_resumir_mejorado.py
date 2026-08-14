# Databricks notebook source
# DBTITLE 1,Overview
# MAGIC %md
# MAGIC # Resumen mejorado
# MAGIC
# MAGIC Este notebook mantiene la lógica del original, pero organizado con mejores prácticas:
# MAGIC
# MAGIC * configuración agrupada al inicio
# MAGIC * lectura, agregación y escritura separadas
# MAGIC * validación liviana del resultado
# MAGIC * estructura clara para una capa gold
# MAGIC

# COMMAND ----------

# DBTITLE 1,Load parameters
# MAGIC %run ./config/parameters

# COMMAND ----------

# DBTITLE 1,Imports
from pyspark.sql.functions import sum

# COMMAND ----------

# DBTITLE 1,Setup section
# MAGIC %md
# MAGIC ## 1. Configuración
# MAGIC
# MAGIC Definimos tablas de entrada y salida para la generación del resumen en la capa gold.
# MAGIC

# COMMAND ----------

# DBTITLE 1,Define configuration
CATALOG = params['catalog']
PREFIX = params['prefix']

table_transform = f'{CATALOG}.silver.{PREFIX}_spark_transform'
table_summary = f'{CATALOG}.gold.{PREFIX}_spark_summary'

print(f'CATALOG: {CATALOG}')
print(f'PREFIX: {PREFIX}')
print(f'Source table: {table_transform}')
print(f'Target table: {table_summary}')

# COMMAND ----------

# DBTITLE 1,Read section
# MAGIC %md
# MAGIC ## 2. Lectura
# MAGIC
# MAGIC Leemos la tabla transformada desde la capa silver.
# MAGIC

# COMMAND ----------

# DBTITLE 1,Read source table
df_transform = spark.table(table_transform)
print('Source table loaded successfully')

# COMMAND ----------

# DBTITLE 1,Summary section
# MAGIC %md
# MAGIC ## 3. Resumen
# MAGIC
# MAGIC Agrupamos por producto y calculamos la suma total para cada uno.
# MAGIC

# COMMAND ----------

# DBTITLE 1,Build summary table
df_summary = (
    df_transform
    .groupBy('producto')
    .agg(sum('total').alias('total_sum'))
)

# COMMAND ----------

# DBTITLE 1,Load section
# MAGIC %md
# MAGIC ## 4. Carga
# MAGIC
# MAGIC Persistimos el resultado resumido en la capa gold.
# MAGIC

# COMMAND ----------

# DBTITLE 1,Write summary table
(
    df_summary.write
    .format('delta')
    .mode('overwrite')
    .saveAsTable(table_summary)
)

print(f'Data written to {table_summary}')

# COMMAND ----------

# DBTITLE 1,Validation section
# MAGIC %md
# MAGIC ## 5. Validación
# MAGIC
# MAGIC Mostramos una vista previa liviana del resultado escrito.
# MAGIC

# COMMAND ----------

# DBTITLE 1,Validate output
target_df = spark.table(table_summary)
preview_df = target_df.limit(5)

print(f'Validation preview for {table_summary}')
print(f'Columns: {target_df.columns}')
display(preview_df)

# COMMAND ----------

