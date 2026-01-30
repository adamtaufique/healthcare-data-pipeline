# Databricks notebook source
# MAGIC %sql
# MAGIC -- Create three-layer architecture
# MAGIC CREATE DATABASE IF NOT EXISTS bronze
# MAGIC COMMENT 'Raw data layer - data as-is from source';
# MAGIC
# MAGIC CREATE DATABASE IF NOT EXISTS silver  
# MAGIC COMMENT 'Cleaned and standardized data';
# MAGIC
# MAGIC CREATE DATABASE IF NOT EXISTS gold
# MAGIC COMMENT 'Business-ready analytics and aggregations';
# MAGIC
# MAGIC -- Verify
# MAGIC SHOW DATABASES;

# COMMAND ----------

# Create directory in DBFS (Databricks File System)
dbutils.fs.mkdirs("/FileStore/healthcare_project/raw")

# List to verify
display(dbutils.fs.ls("/FileStore/"))