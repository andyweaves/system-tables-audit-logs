# Databricks notebook source
# MAGIC %pip install -r ../requirements.txt --upgrade

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./functions

# COMMAND ----------

sql_queries = read_json_file(json_file="../resources/queries_and_alerts.json")["queries_and_alerts"]

databricks_sql_helper = DatabricksSQLHelper()

for q in sql_queries:

 databricks_sql_helper.create_sql_query_and_alert(query=q)

# COMMAND ----------

clean_up = False

if clean_up:
  directories = [x for pair in set([(sql.get("parent"), sql.get("alert").get("parent")) for sql in sql_queries]) for x in pair] 
  databricks_sql_helper.delete_directories(directories)
