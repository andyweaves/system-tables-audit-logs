# system-tables-audit-logs

Automatic creation of important SQL Queries &amp; Alerts for Databricks System Tables `system.access.audit` logs. See the docs for more information:

* [AWS Docs](https://docs.databricks.com/administration-guide/system-tables/audit-logs.html)
* [Azure Docs](https://learn.microsoft.com/en-gb/azure/databricks/administration-guide/system-tables/audit-logs)

## Setup 

### Using notebook

1. Clone this Github Repo using Databricks Repos (see the docs for [AWS](https://docs.databricks.com/repos/index.html) and [Azure](https://docs.microsoft.com/en-us/azure/databricks/repos/))
2. Run the [create_queries_and_alerts](notebooks/create_queries_and_alerts.py) notebook
3. The notebook will create SQL queries and alerts based on the config file [queries_and_alerts.json](resources/queries_and_alerts.json)
4. Once the notebook has been run you should see an HTML table with links to all of the queries and alerts:

![image](https://github.com/andyweaves/system-tables-audit-logs/assets/43955924/59c08671-c060-40d7-8803-5455734ef1bb)

5. To add new SQL queries and alerts, you just add them to the config file [queries_and_alerts.json](resources/queries_and_alerts.json)
6. If you want to cleanup the queries and alerts that have been created, just update the last cell in [create_queries_and_alerts](notebooks/create_queries_and_alerts.py) so that `clean_up = True`

### Using Terraform

Alternatively you can setup everything by following instructions in the [terraform](terraform) folder.  Terraform code is also using data from the config file [queries_and_alerts.json](resources/queries_and_alerts.json) to create all objects.

## Queries and Alerts

The [create_queries_and_alerts](notebooks/create_queries_and_alerts.py) notebook currently creates the following SQL queries and alerts:

<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th style="background-color: #FFFFFF;font-family: Century Gothic, sans-serif;font-size: medium;color: #305496;text-align: left;border-bottom: 2px solid #305496;padding: 0px 20px 0px 0px;width: auto">query_name</th>
      <th style="background-color: #FFFFFF;font-family: Century Gothic, sans-serif;font-size: medium;color: #305496;text-align: left;border-bottom: 2px solid #305496;padding: 0px 20px 0px 0px;width: auto">query_description</th>
      <th style="background-color: #FFFFFF;font-family: Century Gothic, sans-serif;font-size: medium;color: #305496;text-align: left;border-bottom: 2px solid #305496;padding: 0px 20px 0px 0px;width: auto">alert_name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">repeated_failed_login_attempts</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Repeated failed login attempts could indicate an attacker trying to brute force access to your lakehouse. The following query can be used to detect repeated failed login attempts over a 60 minute period within the last 24 hours.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">repeated_failed_login_attempts</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">failed_login_attempts_last_90_days</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Repeated failed login attempts could indicate an attacker trying to brute force access to your lakehouse.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">changes_to_admin_users</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Databricks account and workspace admins should be limited to a few very trusted individuals responsible for managing the deployment. The granting of new admin privileges should be reviewed. The following query can be used to detect changes to admin users within the last 24 hours.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">changes_to_admin_users</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">changes_to_workspace_configuration</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Many workspace-level configurations perform a security-enforcing function. The following SQL query can be used to detect changes in workspace configuration within the last 24 hours.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">changes_to_workspace_configuration</td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">data_downloads_from_control_plane</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Databricks allows customers to configure whether they want users to be able to download notebook or SQL query results, but some customers might want to monitor and report rather than prevent entirely. The following query can be used to detect high numbers of downloads of results from notebooks, Databricks SQL, Unity Catalog volumes and MLflow, as well as the exporting of notebooks in formats that may contain query results within the last 24 hours.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">data_downloads_from_control_plane</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">data_downloads_from_control_plane_last_90_days</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Spikes in the number of downloads could indicate attempts to exfiltrate data.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">ip_access_list_failures</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Databricks allows customers to configure IP Access Lists to restrict access to their account &amp; workspaces. However, they may want to monitor and be alerted whenever access is attempted from an untrusted network. The following query can be used to detect all IpAccessDenied and accountIpAclsValidationFailed events within the last 24 hours.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">ip_access_list_failures</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">ip_access_list_failures_last_90_days</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Repeated IP access list failures could indicate attempts to brute force access to your lakehouse, or internal users trying to connect from untrusted networks.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">ip_access_list_changes</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Databricks allows customers to configure IP access lists to restrict access to their account &amp; workspaces. However, they may want to monitor and be alerted whenever thos IP access lists change. The following query can be used to detect all createIpAccessList, deleteIpAccessList and updateIpAccessList events within the last 24 hours.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">ip_access_list_changes</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">databricks_access_to_customer_workspaces</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">This query can be used to detect logins to your workspace via the Databricks support process. This access is tied to a support ticket while also complying with your workspace configuration that may disable such access. The following query can be used to detect Databricks access to your workspaces within the last 24 hours.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">databricks_access_to_customer_workspaces</td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">databricks_access_to_customer_workspaces_last_90_days</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">All logins to your workspace via the Databricks support process. This access is tied to a support ticket while also complying with your workspace configuration that may disable such access.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">terms_of_service_changes</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">As Databricks rolls out new products and features, customers may occassionally have to agree to changes in our Terms of Service before they can opt-in to the new feature. Some customers might want to monitor when an account admin accepts such terms of service changes. The following SQL query can be used to detect any acceptance or sending of Terms of Service changes within the last 24 hours</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">terms_of_service_changes</td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">account_settings_changes</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Many account-level settings perform a security-enforcing function. The following SQL query can be used to detect changes in account level settings within the last 24 hours.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">account_settings_changes</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">global_init_script_changes</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Global init scripts run arbitrary code that is executed on every cluster. This can be a very powerful capability but with great power comes great responsibility. The following SQL query can be used to detect the creation, update and deletion of global init scripts within the last 24 hours.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">global_init_script_changes</td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">install_library_on_all_clusters</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Installing libraries on all clusters is an anti-pattern. Customers should use cluster-scoped or notebook-scoped libraries for many different reasons including but not limited to transparency, recreatability, reliability and security. The following SQL query can be used to detect any attempts to install libraries on all clusters within the last 24 hours.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">install_library_on_all_clusters</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">mount_point_creation</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Mount points are considered an anti-pattern because mount points do not have the same strong data governance features as external locations or volumes in Unity Catalog. The following query can be used to detect new mount points created or changed within the last 24 hours</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">mount_point_creation</td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">long_lifetime_token_generation</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Personal access tokens should be treated like a credential and protected at all times. As well as being managed by the Token Management API and secured with additional protections like IP Access Lists, they should only be generated with a short lifetime. The following SQL query can be used to detect the generation of PAT tokens with a lifetime of greater than 72 hours.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">long_lifetime_token_generation</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">destructive_activities</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">A high number of destructive activities (such as delete* events) may indicate a malicious attempt to cause disruption and harm. The following SQL query can be used to detect users who have attempted a high number (&gt;50) destructive activities within the last 24 hours. This query filters out activities from Databricks System-Users, although you could optionally add them back in.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">destructive_activities</td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">destructive_activities_last_90_days</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">A spike in the number of destructive activities (such as delete* events) may indicate a malicious attempt to cause disruption and harm.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">potential_privilege_escalation</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">A high number of permission changes could indicate privelege escalation. The following SQL query can be used to detect users who have made a high number (&gt;25) within an hour period over the last 24 hours. This query filters out changes made by Databricks System-Users, although you could optionally add them back in.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">potential_privilege_escalation</td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">potential_privilege_escalation_last_90_days</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">A spike in the number of permission changes could indicate privilege escalation.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">repeated_access_to_secrets</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Repeated attempts to access secrets could indicate an attempt to steal credentials. The following SQL query can be used to detect users who have attempted a high number (&gt;10) of attempts to access secrets within an hour period over the last 24 hours. This query filters out requests from Databricks System-Users, although you could optionally add them back in.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">repeated_access_to_secrets</td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">access_to_secrets_last_90_days</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">A spike in the number of requests to access secrets could indicate attempts to steal credentials.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">access_to_multiple_workspaces</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">The same user accessing multiple workspaces within a short time frame could indicate lateral movement, or malicious attempts to increase the blast radius of an attack. The following SQL query can be used to detect users who have accessed a high number (&gt;5) of different workspaces within the last 24 hours. This query filters out requests from unknown and Databricks System-Users, although you could optionally add them back in.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">access_to_multiple_workspaces</td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">use_of_print_statements</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Databricks supports verbose audit logging, which can be useful in highly regulated environments in which all commands run interactively by a user must be recorded. Verbose audit logs can also be useful for monitoring compliance with coding standards. For example, let's suppose your organization has a policy that print() statements should not be used, the following SQL query could be used to monitor compliance with such a policy by detecting uses of the print() statement within the last 24 hours.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">use_of_print_statements</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">ip_addresses_used_to_access_databricks</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">The following SQL query will show you which IP addresses and the number of requests for each have been used to access your workspace or account over the last 90 days.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">ip_address_ranges_used_to_access_databricks</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">The following SQL query will show you which IP address ranges and the number of requests for each have been used to access your workspaces or account over the last 90 days.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">repeated_unauthorized_uc_requests</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Repeated unauthorized UC requests could indicate privilege escalation, data exfiltration attempts or an attacker trying to brute force access to your data. The following query can be used to detect repeated unauthorized UC requests over a 60 minute period within the last 24 hours.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">repeated_unauthorized_uc_requests</td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">repeated_unauthorized_uc_data_requests</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Repeated unauthorized UC data requests could indicate privilege escalation, data exfiltration attempts or an attacker trying to brute force access to your data. The following query can be used to detect repeated unauthorized UC data access ('generateTemporaryTableCredential', 'generateTemporaryPathCredential', 'generateTemporaryVolumeCredential', 'deltaSharingQueryTable', 'deltaSharingQueryTableChanges') requests over a 60 minute period within the last 24 hours.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">repeated_unauthorized_uc_data_requests</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">unauthorized_uc_data_requests_last_90_days</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Repeated unauthorized UC data requests could indicate privilege escalation, data exfiltration attempts or an attacker trying to brute force access to your data.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">high_number_of_read_writes</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">A high number of read/writes, particularly where the writes are to different locations could indicate data exfiltration attempts. The following  query can be used to detect a high number of read/writes of UC securables (&gt;20) within an hour window over the last 24 hours, particularly where the user is writing to different locations to the reads.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">high_number_of_read_writes</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">read_writes_last_90_days</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">A spike in the number of read/writes (particularly writes) could indicate attempts to exfiltrate data.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">delta_sharing_recipients_without_ip_acls</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">If you’re sharing personal data, delta sharing recipients should always be secured with IP access lists. The following SQL query can be used to detect the creation or update of delta sharing recipients which do not have IP access lists defined within the last 24 hours.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">delta_sharing_recipients_without_ip_acls</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">delta_sharing_ip_access_list_failures</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">If you’re sharing personal data, delta sharing recipients should always be secured with IP access lists. The following SQL query can be used to detect Delta Sharing data access requests ('deltaSharingQueryTable', 'deltaSharingQueryTableChanges') which have failed IP access list checks within the last 24 hours.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">delta_sharing_ip_access_list_failures</td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">delta_sharing_recipient_token_lifetime_change</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Delta Sharing recipient tokens are valid for the lifetime that you specify. As well as protecting Delta Shares via IP access lists, you should also ensure that the lifetime of a recipient token is set to a value that is suitable for the data within the metastore it is accessing. Once you have set a token lifetime, you may want to monitor whether an account admin ever changes that value. The following SQL can be used to detect changes to the Delta Sharing recipient token lifetime for a metastore within the last 24 hours.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">delta_sharing_recipient_token_lifetime_change</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">most_popular_data_products_last_90_days</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Databricks Unity Catalog is the industry’s first unified governance solution for data and AI on the lakehouse. The main benefit of this unification is that you can define once and secure everywhere, but it also means that appropriately privileged users can report on the most popular data products across an organisation. The following SQL query will show you the most popular data assets by number of requests over the last 90 days.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">most_privileged_users</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Identifying our most privileged users can help us to take a risk based approach to security. The following SQL query will provide a relatively simple view of our most privileged users, by showing those with the highest number of different grants to each securable type.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">ip_addresses_used_to_access_uc_data</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">The following SQL query will show you the IP addresses used to access Unity Catalog securables ('generateTemporaryTableCredential', 'generateTemporaryPathCredential', 'generateTemporaryVolumeCredential', 'deltaSharingQueryTable', 'deltaSharingQueryTableChanges') actions over the last 90 days.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">ip_address_ranges_used_to_access_uc_data</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">The following SQL query will show you the IP addresse ranges used to access Unity Catalog securables ('generateTemporaryTableCredential', 'generateTemporaryPathCredential', 'generateTemporaryVolumeCredential', 'deltaSharingQueryTable', 'deltaSharingQueryTableChanges') actions over the last 90 days.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto"></td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">clam_av_infected_files_detected</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Customers using one of our compliance security profile offerings have additional monitoring agents including antivirus installed on their data plane hosts. The following query can be used to detect all antivirus scan events during which infected files have been detected within the last 24 hours.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">clam_av_infected_files_detected</td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">capsule8_container_breakout_events</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">User code runs in low-privileged containers. A container escape could compromise the security of the cluster especially when running with user isolation for Unity Catalog or Table ACLs. Capsule8 provides a few alerts related to container isolation issues that should be investigated if triggered. The following query can be used to detect all container breakout events within the last 24 hours.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">capsule8_container_breakout_events</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">capsule8_changes_to_host_security_settings</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">No untrusted code or end-user commands should be running on the host OS. There should be no process making changes to security configurations of the host VM. The following SQL query can be used to help us identify suspicious changes within the last 24 hours.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">capsule8_changes_to_host_security_settings</td>
    </tr>
    <tr>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">capsule8_kernel_related_events</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Kernel related events could be another indicator of malicious code running on the host. In particular there should be no kernel modules loaded or internal kernel functions being called by user code. The following SQL query can be used to detect any kernel related events within the last 24 hours.</td>
      <td style="background-color: #D9E1F2;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">capsule8_kernel_related_events</td>
    </tr>
    <tr>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">capsule8_suspicious_host_activity</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">Given the architecture of the Databricks containerized runtime and host OS model, only trusted code should be making changes or executing on the host EC2. Changes to containers, evasive actions, or interactive shells could be due to suspicious activity on the host and should be reviewed. The following SQL query can be used to detect suspicious host activity within the last 24 hours.</td>
      <td style="background-color: white; color: black;font-family: Century Gothic, sans-serif;font-size: medium;text-align: left;padding: 0px 20px 0px 0px;width: auto">capsule8_suspicious_host_activity</td>
    </tr>
  </tbody>
</table>
