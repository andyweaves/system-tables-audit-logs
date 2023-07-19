# Databricks notebook source
import json

def read_json_file(json_file: str) -> dict:

  with open(json_file) as f:
    d = json.load(f)
    return d

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.core import DatabricksError
from databricks.sdk.service import sql
from IPython.display import display, HTML
import json


class DatabricksSQLHelper:

  def __init__(self):
    self.workspace_client = WorkspaceClient()
    self.sources = self._get_sources()
    self.base_url = self._get_databricks_workspace_url()
    self.org_id = self._get_databricks_org_id()
    self.html = None

  def _get_context(self):

    return json.loads(dbutils.notebook.entry_point.getDbutils().notebook().getContext().toJson())

  def _get_databricks_workspace_url(self) -> str:
    context = self._get_context()
    return f"{context['tags']['browserHostName']}"

  def _get_databricks_org_id(self) -> str:
    context = self._get_context()
    return f"{context['tags']['orgId']}"

  def _get_sources(self) -> list:
    
    return self.workspace_client.data_sources.list()
  
  def _get_or_create_parent(self, path):

      path = f"/Users/{self.workspace_client.current_user.me().user_name}/{path}"
      self.workspace_client.workspace.mkdirs(path)
      return self.workspace_client.workspace.get_status(path)

  def _create_sql_query(self, query):

    parent = self._get_or_create_parent(path=query["parent"])

    return self.workspace_client.queries.create(
    name=query["name"], 
    data_source_id=self.sources[0].id,
    description=query["description"], 
    query=query["query"],
    parent=f"folders/{parent.object_id}")

  def _create_sql_alert(self, alert, qid):

    parent = self._get_or_create_parent(path=alert["parent"])

    options = sql.AlertOptions(
      column=alert.get("options").get("column"), 
      op=alert.get("options").get("op"), 
      value=alert.get("options").get("value"), 
      custom_subject=alert.get("options").get("custom_subject"), 
      custom_body=alert.get("options").get("custom_body"))

    return self.workspace_client.alerts.create(options=options, query_id=qid, name=alert["name"], parent=f"folders/{parent.object_id}", rearm=alert.get("rearm"))
  
  def _get_html(self) -> HTML:

    return self.html
  
  def get_workspace_client(self) -> WorkspaceClient:

    return self.workspace_client

  def create_sql_query_and_alert(self, query) -> None:

    q = self._create_sql_query(query=query)
    self.html = HTML(f"<b>Created query <a href='https://{self.base_url}/sql/editor/{q.id}?o={self.org_id}'>{q.name}</a>:</b><br>{q.description}")

    alert = query.get("alert")  
    if alert:
      a = self._create_sql_alert(alert=alert, qid=q.id)
      self.html = HTML(f"<b>Created query <a href='https://{self.base_url}/sql/editor/{q.id}?o={self.org_id}'>{q.name}</a> & alert <a href='https://{self.base_url}/sql/alerts/{a.id}?o={self.org_id}'>{a.name}</a>:</b><br>{q.description}")

    return display(self._get_html())

  def _try_to_delete_dir(self, directory):

    print(f"Attempting to delete directory {directory}")
    try:
      self.workspace_client.workspace.delete(directory, recursive=True)
    except DatabricksError as e:
      print(e)

  def delete_directories(self, directories):

    for d in directories:

      path = f"/Users/{self.workspace_client.current_user.me().user_name}/{d}"
      self._try_to_delete_dir(path)
