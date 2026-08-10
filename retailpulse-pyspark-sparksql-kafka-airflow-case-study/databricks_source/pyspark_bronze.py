# Databricks notebook source
from pyspark.sql.functions import lit, current_timestamp, date_trunc

cust_df = (spark.read
      .option("header", "true")
      .csv("/Volumes/workspace/retail_fresher/retail_raw/customers_500.csv")
      .withColumn("source_file", lit("customers_500.csv"))
      .withColumn("ingestion_timestamp", date_trunc("second", current_timestamp()))
)
cust_df.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("workspace.retail_fresher.bronze_customers")

# COMMAND ----------

prod_df = (spark.read
    .option("header", "true")
    .csv("/Volumes/workspace/retail_fresher/retail_raw/products_500.csv")
    .withColumn("source_file", lit("products_500.csv"))
    .withColumn("ingestion_timestamp", date_trunc("second", current_timestamp()))
)
prod_df.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("workspace.retail_fresher.bronze_products")



# COMMAND ----------

order_df = (spark.read
    .option("header", "true")
    .csv("/Volumes/workspace/retail_fresher/retail_raw/sales_orders_500.csv")
    .withColumn("source_file", lit("sales_orders_500.csv"))
    .withColumn("ingestion_timestamp", date_trunc("second", current_timestamp()))
)
order_df.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("workspace.retail_fresher.bronze_sales_orders")