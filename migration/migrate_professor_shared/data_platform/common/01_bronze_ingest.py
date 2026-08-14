# Databricks notebook source
# MAGIC %md
# MAGIC # 01 · Bronze · Ingesta con Auto Loader
# MAGIC
# MAGIC **Dominio**: Operaciones Mineras · Flota de Camiones
# MAGIC **Catalog**: `g6_catalog`  ·  **Schema**: `bronze`
# MAGIC
# MAGIC **Objetivo**: leer los CSV que Airflow deposita en
# MAGIC `abfss://datalake@stdemdsai.dfs.core.windows.net/raw/airflow2/G6/landing/<fuente>/`
# MAGIC y materializarlos como tablas Delta Bronze, preservando la data cruda y
# MAGIC agregando **metadata de linaje**: `_source_file`, `_ingested_at`, `_snapshot_ts`.
# MAGIC
# MAGIC **Patron de nombre**: `<tabla>_<yyyyMMddHHmmss>_<yyyyMMdd>.csv`
# MAGIC
# MAGIC **Estrategia**: Auto Loader (`cloudFiles`) con `trigger(availableNow=True)`.
# MAGIC En cada ejecucion del Job procesa solo los archivos nuevos usando el
# MAGIC checkpoint — no reprocesa lo ya bronceado.

# COMMAND ----------

dbutils.widgets.text("catalog",         "g6_catalog",                       "Catalog")
dbutils.widgets.text("schema",          "bronze",                           "Schema Bronze")
dbutils.widgets.text("storage_account", "stdemdsai",                        "Storage Account")
dbutils.widgets.text("container",       "datalake",                         "Container")
dbutils.widgets.text("landing_root",    "raw/airflow2/G6/landing",          "Landing root (rel. al container)")
dbutils.widgets.text("checkpoint_root", "checkpoints/g6/bronze",            "Checkpoint root (rel. al container)")
dbutils.widgets.text("schema_root",     "schemas/g6/bronze",                "Schema location root (rel. al container)")
dbutils.widgets.text("sources",         "pittruck,stdpitloc,stdtravel",     "Fuentes a ingerir (coma)")

CATALOG   = dbutils.widgets.get("catalog").strip()
SCHEMA    = dbutils.widgets.get("schema").strip()
STG       = dbutils.widgets.get("storage_account").strip()
CONT      = dbutils.widgets.get("container").strip()
LAND_ROOT = dbutils.widgets.get("landing_root").strip().strip("/")
CKPT_ROOT = dbutils.widgets.get("checkpoint_root").strip().strip("/")
SCH_ROOT  = dbutils.widgets.get("schema_root").strip().strip("/")
SOURCES   = [s.strip() for s in dbutils.widgets.get("sources").split(",") if s.strip()]

BASE = f"abfss://{CONT}@{STG}.dfs.core.windows.net"

print(f"Catalog        : {CATALOG}.{SCHEMA}")
print(f"Landing base   : {BASE}/{LAND_ROOT}")
print(f"Checkpoint base: {BASE}/{CKPT_ROOT}")
print(f"Sources        : {SOURCES}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1 · Preparar catalog y schema

# COMMAND ----------

try:
    spark.sql(f"USE CATALOG {CATALOG}")
except Exception as e:
    raise RuntimeError(
        f"El catalog '{CATALOG}' no existe o no tienes USE CATALOG sobre el. "
        f"Pide al admin del metastore que lo cree y te otorgue USE CATALOG + CREATE SCHEMA. "
        f"Detalle: {e}"
    )

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA} "
          f"COMMENT 'Capa Bronze: datos crudos con linaje de ingesta'")
spark.sql(f"USE SCHEMA {SCHEMA}")

print(f"[OK] usando {CATALOG}.{SCHEMA}")

# COMMAND ----------

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG} COMMENT 'Dominio: Operaciones Mineras - Flota de Camiones (Grupo 6)'")
spark.sql(f"CREATE SCHEMA  IF NOT EXISTS {CATALOG}.{SCHEMA} COMMENT 'Capa Bronze: datos crudos con linaje de ingesta'")
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA  {SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2 · Funcion de ingesta con Auto Loader

# COMMAND ----------

from pyspark.sql import functions as F

# Regex tolerante a los dos patrones vistos:
#   pittruck_20231028023538.csv                        <- version corta
#   pittruck_20231026120806_20260712.csv               <- version con fecha de ingesta
SNAPSHOT_REGEX = r".*_(\d{14})(?:_\d{8})?\.csv$"


def ingest_source(source: str) -> None:
    """Ingesta incremental de una carpeta landing/<source> hacia bronze.<source>."""
    landing_path    = f"{BASE}/{LAND_ROOT}/{source}"
    checkpoint_path = f"{BASE}/{CKPT_ROOT}/{source}"
    schema_path     = f"{BASE}/{SCH_ROOT}/{source}"
    target_table    = f"{CATALOG}.{SCHEMA}.{source}"

    print(f"\n=== {source} ===")
    print(f"  landing    : {landing_path}")
    print(f"  checkpoint : {checkpoint_path}")
    print(f"  target     : {target_table}")

    reader = (
        spark.readStream
             .format("cloudFiles")
             .option("cloudFiles.format", "csv")
             .option("cloudFiles.schemaLocation", schema_path)
             .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
             .option("cloudFiles.inferColumnTypes", "false")   # lectura como STRING, casting va en Silver
             .option("header", "true")
             .option("multiLine", "true")
             .option("escape", '"')
             .option("rescuedDataColumn", "_rescued_data")
             .load(landing_path)
    )

    enriched = (
        reader
            .withColumn("_source_file",    F.col("_metadata.file_path"))
            .withColumn("_source_name",    F.col("_metadata.file_name"))
            .withColumn("_ingested_at",    F.current_timestamp())
            .withColumn("_snapshot_ts",
                        F.to_timestamp(
                            F.regexp_extract(F.col("_metadata.file_name"), SNAPSHOT_REGEX, 1),
                            "yyyyMMddHHmmss"
                        ))
            .withColumn("_source",         F.lit(source))
    )

    query = (
        enriched.writeStream
                .format("delta")
                .option("checkpointLocation", checkpoint_path)
                .option("mergeSchema", "true")
                .outputMode("append")
                .trigger(availableNow=True)
                .toTable(target_table)
    )
    query.awaitTermination()

    # Comentario a nivel tabla para el catalogo (dict de datos)
    spark.sql(f"""
        COMMENT ON TABLE {target_table} IS
        'Bronze · {source} · datos crudos ingeridos desde landing con Auto Loader.
         Cada fila es un renglon del CSV original; se agregan columnas de linaje con prefijo _ .'
    """)

    n = spark.table(target_table).count()
    print(f"  filas en bronze: {n:,}")


# COMMAND ----------

# MAGIC %md
# MAGIC ## 3 · Ejecutar por fuente

# COMMAND ----------

for src in SOURCES:
    ingest_source(src)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4 · Documentar columnas de linaje (Unity Catalog · Diccionario)

# COMMAND ----------

LINEAGE_COLUMNS = {
    "_source_file": "Ruta completa del CSV origen en el Data Lake",
    "_source_name": "Nombre del archivo CSV origen",
    "_ingested_at": "Timestamp UTC en que Auto Loader materializo la fila",
    "_snapshot_ts": "Timestamp de negocio extraido del nombre del archivo (yyyyMMddHHmmss)",
    "_source":      "Nombre logico de la fuente (pittruck / stdpitloc / stdtravel)",
    "_rescued_data": "Columnas del CSV que no calzaron con el esquema esperado (JSON)",
}

for src in SOURCES:
    target = f"{CATALOG}.{SCHEMA}.{src}"
    existing_cols = {r["col_name"] for r in spark.sql(f"DESCRIBE TABLE {target}").collect()}
    for col, comment in LINEAGE_COLUMNS.items():
        if col in existing_cols:
            spark.sql(f"ALTER TABLE {target} ALTER COLUMN `{col}` COMMENT '{comment}'")
    print(f"[OK] comentarios aplicados en {target}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5 · Resumen

# COMMAND ----------

rows = []
for src in SOURCES:
    tbl = f"{CATALOG}.{SCHEMA}.{src}"
    cnt = spark.table(tbl).count()
    rows.append((tbl, cnt))

display(spark.createDataFrame(rows, "table STRING, row_count LONG"))