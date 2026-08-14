# Databricks notebook source
import googleapiclient.discovery
import googleapiclient.errors
import configparser

# COMMAND ----------

# Generando variables
api_service_name = 'youtube'
api_version = 'v3'
DEVELOPER_KEY = dbutils.secrets.get(scope="de-scope", key="de-google-key")

# COMMAND ----------

# Construyendo el objeto Youtube
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

# COMMAND ----------

# Generando consulta por comentarios
request = youtube.commentThreads().list(
    part='snippet',
    maxResults=100,
    order="relevance",
    videoId='mBoX_JCKZTE',
)
response = request.execute()

# COMMAND ----------

# Obteniendo datos
list_dict = list()

for item in response['items']:
  comment = item['snippet']['topLevelComment']['snippet']

  dict_tweet = {
      'author': comment['authorDisplayName'],
      'published_at': comment['publishedAt'],
      'updated_at': comment['updatedAt'],
      'like_count': comment['likeCount'],
      'text': comment['textDisplay'],
  }

  list_dict.append(dict_tweet)

print(len(list_dict))

# COMMAND ----------

# Convert list_dict to Spark DataFrame
df_youtube = spark.createDataFrame(list_dict)

# COMMAND ----------

# Create a temporary view
df_youtube.createOrReplaceTempView("vw_youtube_comments")

# COMMAND ----------

# Query the temporary view
result_df = spark.sql("SELECT * FROM vw_youtube_comments")

# Display the result
display(result_df)