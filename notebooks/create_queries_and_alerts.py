# Databricks notebook source
# MAGIC %pip install -r ../requirements.txt --upgrade

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./functions

# COMMAND ----------

sql_queries = read_json_file(json_file="../resources/queries_and_alerts.json")["queries_and_alerts"]

databricks_sql_helper = DatabricksSQLHelper()

# for q in sql_queries:

#  databricks_sql_helper.create_sql_query_and_alert(query=q)

# COMMAND ----------

import pandas as pd
from pretty_html_table import build_table

pdf = (pd.json_normalize(sql_queries)[["name", "description", "alert.name"]]
       .rename(columns={"name": "query_name", "description": "query_description", "alert.name": "alert_name"}))
displayHTML(
  f"""<h2>Created the following SQL Queries and Alerts</h2>
  {build_table(pdf, 'blue_light')}
  """)

# COMMAND ----------

clean_up = False

if clean_up:
  directories = [x for pair in set([(sql.get("parent"), sql.get("alert").get("parent")) for sql in sql_queries]) for x in pair] 
  databricks_sql_helper.delete_directories(directories)
