# Databricks notebook source
# MAGIC %pip install -r ../requirements.txt --upgrade

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./functions

# COMMAND ----------

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

sql_queries = read_json_file(json_file="../resources/queries_and_alerts.json")["queries_and_alerts"]
base_url, org_id = get_databricks_host_and_org_id()

for q in sql_queries:
  create_sql_query(workspace_client=w, query=q, base_url=base_url, org_id=org_id)
