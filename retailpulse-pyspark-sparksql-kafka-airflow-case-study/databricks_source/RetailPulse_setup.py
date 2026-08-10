# Databricks notebook source

spark.sql("CREATE SCHEMA IF NOT EXISTS workspace.retail_fresher")

# COMMAND ----------

spark.sql("CREATE VOLUME IF NOT EXISTS workspace.retail_fresher.retail_raw")