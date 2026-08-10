-- Databricks notebook source
show tables in workspace.retail_fresher


-- COMMAND ----------

SELECT * 
FROM workspace.retail_fresher.silver_sales_orders
WHERE order_status = "COMPLETED"
LIMIT 20;

-- COMMAND ----------

SELECT *
FROM workspace.retail_fresher.silver_sales_orders o
JOIN workspace.retail_fresher.silver_customers c ON c.customer_id = o.customer_id
JOIN workspace.retail_fresher.silver_products p ON p.product_id = o.product_id
LIMIT 20;

-- COMMAND ----------

SELECT
  order_month,
  category,
  ROUND(SUM(net_sales), 2) AS total_net_sales
FROM workspace.retail_fresher.enriched_sales
GROUP BY order_month, category
ORDER BY total_net_sales;

-- COMMAND ----------

SELECT
  city,
  ROUND(SUM(net_sales), 2) AS total_city_sales
FROM workspace.retail_fresher.enriched_sales
GROUP BY city
ORDER BY total_city_sales;

-- COMMAND ----------

SELECT
  customer_id,
  customer_name,
  ROUND(SUM(net_sales), 2) AS total_customer_value
FROM workspace.retail_fresher.enriched_sales
GROUP BY customer_id, customer_name
ORDER BY total_customer_value DESC;

-- COMMAND ----------

SELECT product_name, category, rank
FROM (
  SELECT
    product_name,
    category,
    RANK() OVER (PARTITION BY category ORDER BY net_sales DESC) AS rank
  FROM workspace.retail_fresher.enriched_sales
)
WHERE rank <= 1;