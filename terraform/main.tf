terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}

provider "databricks" {
}

data "databricks_current_user" "me" {}

locals {
  qa_data     = jsondecode(file("../resources/queries_and_alerts.json"))["queries_and_alerts"]
  directories = toset(flatten([for k in local.qa_data : [k.parent, k.alert.parent]]))
  queries     = toset([for k in local.qa_data : k.name])
  data_map    = { for k in local.qa_data : k.name => k }
}

resource "databricks_directory" "this" {
  for_each = local.directories
  path     = "${data.databricks_current_user.me.home}/${each.value}"
}
