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

# for q in sql_queries:

#   print(q)
