# Databricks notebook source
CATALOG = 'gx_catalog'

# COMMAND ----------

table_streaming_predictions = f'{CATALOG}.default.streaming_predictions'
spark.sql(f'DROP TABLE IF EXISTS {table_streaming_predictions}')

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, TimestampType

schema = StructType([
    StructField("user_id", IntegerType(), True),
    StructField("amount", DoubleType(), True),
    StructField("timestamp", TimestampType(), True)
])

# Esta sería la fuente de datos persistente (el stream persistido en Delta)
source_path = "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/fraud/unlabeled/"
model_path = "abfss://datalake@stdemdsai.dfs.core.windows.net/models/fraud/lr_model"

# COMMAND ----------

# MAGIC %md
# MAGIC ### Proceso de Streaming en Tiempo Real (predicciones en línea)

# COMMAND ----------

from pyspark.ml.classification import LogisticRegressionModel
from pyspark.ml.feature import VectorAssembler
from pyspark.sql.functions import col

# Definimos el flujo de datos en streaming
df_stream = (
    spark.readStream
    .format("csv")
    .option("header", "true")
    .schema(schema)
    .load(source_path)
)

# Asumimos que los datos tienen las siguientes columnas: 'user_id', 'amount', 'is_fraud' (etiqueta), 'timestamp'.
# Preprocesamos para preparar los datos para el modelo.
assembler = VectorAssembler(inputCols=["amount"], outputCol="features")
df_features = assembler.transform(df_stream).select("user_id", "features", "timestamp")



# Cargamos el modelo previamente entrenado (si existe)
lr_model = LogisticRegressionModel.load(model_path)

# Hacemos predicciones en línea
df_predictions = lr_model.transform(df_features)

checkpoint_streaming_predictions = "abfss://datalake@stdemdsai.dfs.core.windows.net/_checkpoints/streaming_predictions"
dbutils.fs.rm(checkpoint_streaming_predictions, recurse=True)

# Aquí escribimos las predicciones en una tabla Delta para tener acceso a ellas en tiempo real
(
    df_predictions.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", checkpoint_streaming_predictions)
    .toTable(f"{CATALOG}.default.streaming_predictions")
)

# COMMAND ----------

spark.sql(f'SELECT * FROM {CATALOG}.default.streaming_predictions').display()

# COMMAND ----------

dbutils.fs.cp(
    "abfss://datalake@stdemdsai.dfs.core.windows.net/demo_sources/fraud_data/fraud_data_3.csv",
    "abfss://datalake@stdemdsai.dfs.core.windows.net/raw/fraud/unlabeled/fraud_data_3.csv"
    )

# COMMAND ----------

spark.sql(f'SELECT * FROM {CATALOG}.default.streaming_predictions').display()