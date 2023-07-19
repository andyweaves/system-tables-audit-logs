# system-tables-audit-logs

Automatic creation of important SQL Queries &amp; Alerts for Databricks System Tables `system.access.audit` logs. See the docs for more information:

* [AWS Docs](https://docs.databricks.com/administration-guide/system-tables/audit-logs.html)
* [Azure Docs](https://learn.microsoft.com/en-gb/azure/databricks/administration-guide/system-tables/audit-logs)

## Setup 

1. Clone this Github Repo using Databricks Repos (see the docs for [AWS](https://docs.databricks.com/repos/index.html) and [Azure](https://docs.microsoft.com/en-us/azure/databricks/repos/))
2. Run the [create_queries_and_alerts](notebooks/create_queries_and_alerts) notebook
3. The notebook will create SQL queries and alerts based on the config file [queries_and_alerts.json](resources/queries_and_alerts.json)
4. To add new SQL queries and alerts, you can just add them to the config file [queries_and_alerts.json](resources/queries_and_alerts.json)
5. If you want to cleanup the queries and alerts that have been created, just update the last cell in [create_queries_and_alerts](notebooks/create_queries_and_alerts) so that `clean_up = True`