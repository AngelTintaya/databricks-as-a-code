# Databricks notebook source
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, TimestampType

schema = StructType([
    StructField("user_id", IntegerType(), True),
    StructField("amount", DoubleType(), True),
    StructField("is_fraud", IntegerType(), True),
    StructField("timestamp", TimestampType(), True)
])

# Esta sería la fuente de datos persistente (el stream persistido en Delta)
source_path = "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/fraud/labeled/"
model_path = "abfss://datalake@stdemdsai.dfs.core.windows.net/models/fraud/lr_model"

# COMMAND ----------

# MAGIC %md
# MAGIC ### Proceso Batch Periódico (Reentrenamiento semanal)

# COMMAND ----------

from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import VectorAssembler
from pyspark.ml import Pipeline
from pyspark.sql import functions as F

# Leer los datos históricos (todo el stream persistido hasta ahora)
df_batch = (
    spark.read
    .option("header", "true")
    .schema(schema)
    .csv(source_path)
)

# Preprocesamiento (en este caso solo usamos 'amount' como feature)
assembler = VectorAssembler(inputCols=["amount"], outputCol="features")
df_features_batch = assembler.transform(df_batch).select("user_id", "features", "is_fraud")

# Definir y entrenar el modelo (Logistic Regression)
lr = LogisticRegression(labelCol="is_fraud", featuresCol="features")
lr_model = lr.fit(df_features_batch)

# Borrar ultimo modelo
dbutils.fs.rm(model_path, recurse=True)

# Guardar el modelo entrenado para su uso futuro
lr_model.save(model_path)