# Databricks notebook source
from pyspark.sql.window import Window
from pyspark.sql.functions import (
    col,
    sum,
    rank,
    round,
    countDistinct,
    avg
)

df_joined = spark.table("workspace.retail_fresher.enriched_sales")

# COMMAND ----------

monthly_cat = (df_joined
            .groupBy("order_month", "category")
            .agg(
                round(sum("net_sales"), 2).alias("total_net_sales"), 
                countDistinct("order_id").alias("order_count"),
                round(avg("net_amount"), 2).alias("order_average")
            )
            .orderBy("total_net_sales")
)

monthly_cat.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("workspace.retail_fresher.monthly_category_sales")


# COMMAND ----------

city_sales = (df_joined
            .groupBy("city")
            .agg(round(sum("net_sales"), 2).alias("total_city_sales"))
            .orderBy("total_city_sales")
)

city_sales.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("workspace.retail_fresher.city_sales")


# COMMAND ----------

cust_value = (df_joined
            .groupBy("customer_id", "customer_name")
            .agg(round(sum("net_sales"), 2).alias("total_customer_value"))
            .orderBy(col("total_customer_value").desc())
            
)

cust_value.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("workspace.retail_fresher.customer_value")

# COMMAND ----------

top_prod = (df_joined
            .withColumn("rank", rank().over(Window.partitionBy("category").orderBy(col("net_sales").desc())))
            .filter(col("rank") <= 1)
            .select("product_name", "category", "rank")
)

top_prod.write.mode("overwrite").saveAsTable("workspace.retail_fresher.top_products_by_category")