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
    self.urls = {}

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
  
  def get_workspace_client(self) -> WorkspaceClient:

    return self.workspace_client

  def create_sql_query_and_alert(self, query) -> None:

    q = self._create_sql_query(query=query)
    displayHTML(f"Successfully created query <a href='https://{self.base_url}/sql/editor/{q.id}?o={self.org_id}'>{q.name}</a>")
    self.urls.update({"query_url": 
      f"<a href='https://{self.base_url}/sql/editor/{q.id}?o={self.org_id}'>{q.name}</a>"})

    alert = query.get("alert") 

    if alert:
      a = self._create_sql_alert(alert=alert, qid=q.id)
      displayHTML(f"Successfully created alert <a href='https://{self.base_url}/sql/alerts/{a.id}?o={self.org_id}'>{a.name}</a>")
      self.urls.update({"alert_url": f"<a href='https://{self.base_url}/sql/alerts/{a.id}?o={self.org_id}'>{a.name}</a>"})

    return self.urls

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

# COMMAND ----------

import io

# Modified version of https://github.com/sbi-rviot/ph_table/tree/master so that URLs work and are clickable
# 
# MIT License
#
# Copyright (c) [year] [fullname]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

dict_colors = {
    'yellow_light' : ('#BF8F00', '2px solid #BF8F00', '#FFF2CC', '#FFFFFF'),
    'grey_light' : ('#808080', '2px solid #808080', '#EDEDED', '#FFFFFF'),
    'blue_light' : ('#305496', '2px solid #305496', '#D9E1F2', '#FFFFFF'),
    'orange_light' : ('#C65911', '2px solid #C65911', '#FCE4D6', '#FFFFFF'),
    'green_light' : ('#548235', '2px solid #548235', '#E2EFDA', '#FFFFFF'), 
    'red_light' : ('#823535', '2px solid #823535', '#efdada', '#FFFFFF'),
    'yellow_dark' : ('#FFFFFF', '2px solid #BF8F00', '#FFF2CC', '#BF8F00'),
    'grey_dark' : ('#FFFFFF', '2px solid #808080', '#EDEDED', '#808080'),
    'blue_dark': ('#FFFFFF', '2px solid #305496', '#D9E1F2', '#305496'),
    'orange_dark' : ('#FFFFFF', '2px solid #C65911', '#FCE4D6', '#C65911'),
    'green_dark' : ('#FFFFFF', '2px solid #548235', '#E2EFDA', '#548235'),
    'red_dark' : ('#FFFFFF', '2px solid #823535', '#efdada', '#823535')
}


def build_table(
        df, 
        color, 
        font_size='medium', 
        font_family='Century Gothic, sans-serif', 
        text_align='left', 
        width='auto', 
        index=False, 
        even_color='black', 
        even_bg_color='white', 
        odd_bg_color=None,
        border_bottom_color=None,
        escape=False,
        render_links=True,
        width_dict=[],
        padding="0px 20px 0px 0px",
        float_format=None,
        conditions={}):

    if df.empty:
      return ''
     
    # Set color
    color, border_bottom, odd_background_color, header_background_color = dict_colors[color]

    if odd_bg_color:
        odd_background_color = odd_bg_color

    if border_bottom_color:
        border_bottom = border_bottom_color 

    a = 0
    while a != len(df):
        if a == 0:        
            df_html_output = df.iloc[[a]].to_html(
                na_rep="", 
                index=index, 
                border=0, 
                escape=escape, 
                float_format=float_format,
                render_links=render_links
            )
            # change format of header
            if index:
                df_html_output = df_html_output.replace('<th>'
                                                        ,'<th style = "background-color: ' + header_background_color
                                                        + ';font-family: ' + font_family
                                                        + ';font-size: ' + str(font_size)
                                                        + ';color: ' + color
                                                        + ';text-align: ' + text_align
                                                        + ';border-bottom: ' + border_bottom
                                                        + ';padding: ' + padding
                                                        + ';width: ' + str(width) + '">', len(df.columns)+1)

                df_html_output = df_html_output.replace('<th>'
                                                        ,'<th style = "background-color: ' + odd_background_color
                                                        + ';font-family: ' + font_family
                                                        + ';font-size: ' + str(font_size)
                                                        + ';text-align: ' + text_align
                                                        + ';padding: ' + padding
                                                        + ';width: ' + str(width) + '">')

            else:
                df_html_output = df_html_output.replace('<th>'
                                                        ,'<th style = "background-color: ' + header_background_color
                                                        + ';font-family: ' + font_family
                                                        + ';font-size: ' + str(font_size)
                                                        + ';color: ' + color
                                                        + ';text-align: ' + text_align
                                                        + ';border-bottom: ' + border_bottom
                                                        + ';padding: ' + padding
                                                        + ';width: ' + str(width) + '">')

            #change format of table
            df_html_output = df_html_output.replace('<td>'
                                                    ,'<td style = "background-color: ' + odd_background_color
                                                    + ';font-family: ' + font_family
                                                    + ';font-size: ' + str(font_size)
                                                    + ';text-align: ' + text_align
                                                    + ';padding: ' + padding
                                                    + ';width: ' + str(width) + '">')
            body = """<p>""" + format(df_html_output)

            a = 1

        elif a % 2 == 0:
            df_html_output = df.iloc[[a]].to_html(na_rep = "", index = index, header = False, escape=escape, render_links=render_links)
             
            # change format of index
            df_html_output = df_html_output.replace('<th>'
                                                    ,'<th style = "background-color: ' + odd_background_color
                                                    + ';font-family: ' + font_family
                                                    + ';font-size: ' + str(font_size)
                                                    + ';text-align: ' + text_align
                                                    + ';padding: ' + padding
                                                    + ';width: ' + str(width) + '">')

            #change format of table
            df_html_output = df_html_output.replace('<td>'
                                                    ,'<td style = "background-color: ' + odd_background_color
                                                    + ';font-family: ' + font_family
                                                    + ';font-size: ' + str(font_size)
                                                    + ';text-align: ' + text_align
                                                    + ';padding: ' + padding
                                                    + ';width: ' + str(width) + '">')

            body = body + format(df_html_output)

            a += 1       

        elif a % 2 != 0:
            df_html_output = df.iloc[[a]].to_html(na_rep = "", index = index, header = False, escape=escape, render_links=render_links)
             
            # change format of index
            df_html_output = df_html_output.replace('<th>'
                                                    ,'<th style = "background-color: ' + even_bg_color
                                                    + '; color: ' + even_color
                                                    + ';font-family: ' + font_family
                                                    + ';font-size: ' + str(font_size)
                                                    + ';text-align: ' + text_align
                                                    + ';padding: ' + padding
                                                    + ';width: ' + str(width) + '">')
             
            #change format of table
            df_html_output = df_html_output.replace('<td>'
                                                    ,'<td style = "background-color: ' + even_bg_color
                                                    + '; color: ' + even_color
                                                    + ';font-family: ' + font_family
                                                    + ';font-size: ' + str(font_size)
                                                    + ';text-align: ' + text_align
                                                    + ';padding: ' + padding
                                                    + ';width: ' + str(width) + '">')
            body = body + format(df_html_output)

            a += 1

    body = body + """</p>"""

    body = body.replace("""</td>
    </tr>
  </tbody>
</table>
            <table border="1" class="dataframe">
  <tbody>
    <tr>""","""</td>
    </tr>
    <tr>""").replace("""</td>
    </tr>
  </tbody>
</table><table border="1" class="dataframe">
  <tbody>
    <tr>""","""</td>
    </tr>
    <tr>""")

    if conditions:
        for k in conditions.keys():
            try:
                conditions[k]['index'] = list(df.columns).index(k)
                width_body = ''
                w = 0
                for line in io.StringIO(body):
                    updated_body = False
                    if  w == conditions[k]['index']:
                        try:
                            if int(repr(line).split('>')[1].split('<')[0]) < conditions[k]['min']:
                                if 'color: black' in repr(line):
                                    width_body = width_body + repr(line).replace("color: black", 'color: ' + conditions[k]['min_color'])[1:]
                                elif 'color: white' in repr(line):
                                    width_body = width_body + repr(line).replace("color: white", 'color: ' + conditions[k]['min_color'])[1:]
                                else:
                                    width_body = width_body + repr(line).replace('">', '; color: ' + conditions[k]['min_color'] + '">')[1:]
                                updated_body = True
                            elif int(repr(line).split('>')[1].split('<')[0]) > conditions[k]['max']:
                                if 'color: black' in repr(line):
                                    width_body = width_body + repr(line).replace("color: black", 'color: ' + conditions[k]['max_color'])[1:]
                                elif 'color: white' in repr(line):
                                    width_body = width_body + repr(line).replace("color: white", 'color: ' + conditions[k]['max_color'])[1:]
                                else:
                                    width_body = width_body + repr(line).replace('">', '; color: ' + conditions[k]['max_color'] + '">')[1:]
                                updated_body = True
                        except:
                            pass
                    if not updated_body:
                        width_body = width_body + repr(line)[1:]

                    if str(repr(line))[:10] == "'      <td" or str(repr(line))[:10] == "'      <th":
                        if w == len(df.columns) -1:
                            w = 0
                        else:
                            w += 1
                body = width_body[:len(width_body)-1]
            except:
                pass

    if len(width_dict) == len(df.columns):
        width_body = ''
        w = 0
        if conditions:
            for line in body.split(r"\n'"):
                width_body = width_body + repr(line).replace("width: auto", 'width: ' + width_dict[w])[1:]
                if str(repr(line))[:10] == "'      <td" or str(repr(line))[:10] == "'      <th" :
                    if w == len(df.columns) -1:
                        w = 0
                    else:
                        w += 1
        else:
            for line in io.StringIO(body):
                line = line.replace("\n", "")
                width_body = width_body + repr(line).replace("width: auto", 'width: ' + width_dict[w])[1:]
                if str(repr(line))[:10] == "'      <td" or str(repr(line))[:10] == "'      <th" :
                    if w == len(df.columns) -1:
                        w = 0
                    else:
                        w += 1
        return width_body[:len(width_body)-1].replace("'", "")
    else:
        return body.replace(r"\n'", "")
