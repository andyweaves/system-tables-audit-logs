# Databricks notebook source
import json

def read_json_file(json_file: str) -> dict:

  with open(json_file) as f:
    d = json.load(f)
    return d

# COMMAND ----------

def get_databricks_host_and_org_id():

  context = json.loads(dbutils.notebook.entry_point.getDbutils().notebook().getContext().toJson())
  return f"{context['tags']['browserHostName']}", f"{context['tags']['orgId']}"

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import sql
from IPython.display import display, HTML

def create_sql_query(workspace_client: WorkspaceClient, query: dict, base_url: str, org_id: str) -> None:

  sources = workspace_client.data_sources.list()

  path = f"/Users/{workspace_client.current_user.me().user_name}/{query['parent']}"
  workspace_client.workspace.mkdirs(path)
  parent = workspace_client.workspace.get_status(path)
  q = workspace_client.queries.create(
    name=query["name"], 
    data_source_id=sources[0].id,
    description=query["description"], 
    query=query["query"],
    parent=f"folders/{parent.object_id}")
  
  html = None
  
  if query.get("alert"): 

    alert = query["alert"]
    path = f"/Users/{workspace_client.current_user.me().user_name}/{alert.get('parent')}"
    workspace_client.workspace.mkdirs(path)
    parent = workspace_client.workspace.get_status(path)

    options = sql.AlertOptions(
      column=alert.get("options").get("column"), 
      op=alert.get("options").get("op"), 
      value=alert.get("options").get("value"), 
      custom_subject=alert.get("options").get("custom_subject"), 
    custom_body=alert.get("options").get("custom_body"))

    a = workspace_client.alerts.create(options=options, query_id=q.id, name=alert["name"], parent=f"folders/{parent.object_id}", rearm=alert.get("rearm"))

    html = HTML(f"<b>Created query <a href='https://{base_url}/sql/editor/{q.id}?o={org_id}'>{q.name}</a> & alert <a href='https://{base_url}/sql/alerts/{a.id}?o={org_id}'>{a.name}</a>:</b><br>{q.description}")

  else:
    html = HTML(f"<b>Created query <a href='https://{base_url}/sql/editor/{q.id}?o={org_id}'>{q.name}</a>:</b><br>{q.description}")
  
  return display(html)
