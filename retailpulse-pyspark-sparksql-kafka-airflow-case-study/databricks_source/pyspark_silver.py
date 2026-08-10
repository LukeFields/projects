# Databricks notebook source
from pyspark.sql.functions import (
    col,
    trim,
    when,
    count,
    lower,
    upper,
    to_date,
    to_timestamp,
    row_number,
    date_format,
    datediff,
    round
)
from pyspark.sql.window import Window

cust_df = spark.table("workspace.retail_fresher.bronze_customers")
prod_df = spark.table("workspace.retail_fresher.bronze_products")
order_df = spark.table("workspace.retail_fresher.bronze_sales_orders")

# COMMAND ----------

cust_city = cust_df.withColumn(
    "city",
    when((col("city").isNull()) | (trim(col("city")) == ""), "Unknown")
    .otherwise(col("city"))
)


# COMMAND ----------

ignored_cols = ["source_file", "ingestion_timestamp"]
cust_lower = cust_city.withColumn("email", lower(col("email")))
cust_trimmed = cust_lower.withColumns({c: trim(col(c)).alias(c) for c in cust_lower.columns if c not in ignored_cols})

prod_trimmed = prod_df.withColumns({c: trim(col(c)).alias(c) for c in prod_df.columns if c not in ignored_cols})

order_upper = order_df.withColumns({c: upper(col(c)) for c in ("payment_method", "order_status", "sales_channel")})
order_trimmed = order_upper.withColumns({c: trim(col(c)).alias(c) for c in order_upper.columns if c not in ignored_cols})

# COMMAND ----------

cust_casted = (cust_trimmed
            .withColumn("signup_date", col("signup_date").try_cast("date"))
            .withColumn("date_of_birth", col("date_of_birth").try_cast("date"))
            .withColumn("loyalty_points", col("loyalty_points").try_cast("int"))
            .withColumn("updated_at", col("updated_at").try_cast("timestamp"))
)
prod_casted = (prod_trimmed
            .withColumn("unit_price", col("unit_price").try_cast("double"))
            .withColumn("cost_price", col("cost_price").try_cast("double"))
            .withColumn("stock_quantity", col("stock_quantity").try_cast("int"))
            .withColumn("launch_date", col("launch_date").try_cast("date"))
            .withColumn("product_rating", col("product_rating").try_cast("double"))
)
order_casted = (order_trimmed
            .withColumn("order_timestamp", col("order_timestamp").try_cast("timestamp"))
            .withColumn("quantity", col("quantity").try_cast("int"))
            .withColumn("discount_pct", col("discount_pct").try_cast("int"))
            .withColumn("promised_delivery_date", col("promised_delivery_date").try_cast("date"))
            .withColumn("actual_delivery_date", col("actual_delivery_date").try_cast("date"))
)

# COMMAND ----------

cust_deduped = (cust_casted
            .withColumn("row_number", row_number().over(Window.partitionBy("customer_id").orderBy(col("updated_at").desc())))
            .filter(col("row_number") == 1)
            .drop("row_number")
)
cust_filtered = (cust_deduped
            .withColumnsRenamed({"ingestion_timestamp": "customer_ingestion_timestamp", "source_file": "customer_source_file"})
            .filter(col("is_active") == "Y")
)


# COMMAND ----------

prod_filtered = (prod_casted
            .withColumnsRenamed({"ingestion_timestamp": "product_ingestion_timestamp", "source_file": "product_source_file"})
            .filter(col("unit_price") > 0)
            .filter(col("cost_price") > 0)
            .filter(upper(col("active_flag")) == "Y")
            .filter(col("product_id").isNotNull())
)

# COMMAND ----------

order_filtered = (order_casted
            .withColumnsRenamed({"ingestion_timestamp": "order_ingestion_timestamp", "source_file": "order_source_file"})
            .filter(col("order_id").isNotNull())
            .filter(col("customer_id").isNotNull())
            .filter(col("product_id").isNotNull())
            .filter(col("quantity") > 0)
            .filter(col("discount_pct") <= 100)
            .filter(col("discount_pct") >= 0)
            .filter(col("payment_method").isNotNull())
)


# COMMAND ----------

cust_filtered.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("workspace.retail_fresher.silver_customers")
prod_filtered.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("workspace.retail_fresher.silver_products")
order_filtered.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("workspace.retail_fresher.silver_sales_orders")

# COMMAND ----------

df_joined = (cust_filtered.alias("c")
            .join(order_filtered.alias("o"), on="customer_id", how="inner")
            .join(prod_filtered.alias("p"), on="product_id", how="inner")
            .withColumn("gross_amount", round(col("quantity") * col("unit_price"), 2))
            .withColumn("discount_amount", round(col("gross_amount") * (col("discount_pct") / 100.0), 2))
            .withColumn("net_amount", round(col("gross_amount") - col("discount_amount"), 2))
            .withColumn("net_sales", when(col("o.order_status") == "COMPLETED", round(col("net_amount"), 2)).otherwise(0))
            .withColumn("profit_per_unit", round(col("unit_price") - col("cost_price"), 2))
            .withColumn("delivery_days", datediff(col("actual_delivery_date"), col("order_timestamp")))
            .withColumn("late_delivery_flag", when(col("actual_delivery_date") > col("promised_delivery_date"), "Y").otherwise("N"))
            .withColumn("order_month", date_format(col("o.order_timestamp"), "yyyy-MM"))
)
df_joined.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("workspace.retail_fresher.enriched_sales")