# Terraform code for assets creation

The code in this folder could be used to create following Databricks objects based on information from the config file [queries_and_alerts.json](../resources/queries_and_alerts.json):

* Directories in Databricks workspace as subfolders of the current user's home.
* Optional Databricks SQL Warehouse (you have an option to provide an ID of an existing SQL Warehouse)
* Databricks SQL Queries.
* Databricks SQL Alerts.
* Databricks job that will check alerts every hour.

## Setup

1. Either modify the provider block for `databricks` provider in the `main.tf` to specify [authentication options](https://registry.terraform.io/providers/databricks/databricks/latest/docs#authentication)), or set corresponding [environment variables](https://registry.terraform.io/providers/databricks/databricks/latest/docs#environment-variables).
1. Create the `terraform.tfvars` file and put following variables into it:
  * `alert_emails` - list of email addresses to alert when alert is triggered.
  * `warehouse_id` - the ID of an existing Databricks SQL Warehouse if you don't want to create new one.  If not specified, new SQL Warehouse will be created.
1. Execute `terraform plan` to check that everything is configure correctly.
1. Execute `terraform apply` to create all objects.

