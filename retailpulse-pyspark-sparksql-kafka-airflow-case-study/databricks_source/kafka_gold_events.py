# Databricks notebook source
from pyspark.sql import functions as F
import json

output_path = "/Volumes/workspace/retail_fresher/retail_raw"

summary_df = spark.read.table(
    f"workspace.retail_fresher.monthly_category_sales"
)

# COMMAND ----------

events_df = (
    summary_df
    .select(
        F.concat(
            F.col("order_month"),
            F.lit("-"),
            F.regexp_replace(F.col("category"), " ", "_")
        ).alias("event_id"),
        F.lit("MONTHLY_CATEGORY_SALES_READY").alias("event_type"),
        F.current_timestamp().alias("event_timestamp"),
        "order_month",
        "category",
        "total_net_sales",
        "order_count",
        "order_average",
    )
)

# COMMAND ----------

(
    events_df.write
    .mode("overwrite")
    .option("overwriteSchema", True)
    .saveAsTable("workspace.retail_fresher.gold_kafka_events")
)

# COMMAND ----------

dbutils.fs.rm(output_path + "/kafka_events.jsonl", recurse=True)

events_df.coalesce(1).write.mode("overwrite").json(output_path + "/kafka_events")

file = [f for f in dbutils.fs.ls(output_path + "/kafka_events") if f.name.endswith(".json")]
dbutils.fs.mv(file[0].path, output_path + "/kafka_events.jsonl")

dbutils.fs.rm(output_path + "/kafka_events", recurse=True)