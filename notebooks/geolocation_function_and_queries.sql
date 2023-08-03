-- Databricks notebook source
-- MAGIC %md
-- MAGIC ## Setup
-- MAGIC 1. Sign up for [GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
-- MAGIC 2. Download the relevant database files
-- MAGIC 3. Download the [GeoIP CSV convertor](https://github.com/maxmind/geoip2-csv-converter)
-- MAGIC 4. Run the geoip2-csv-converter to convert the relevant database files. For example: ```./geoip2-csv-converter -block-file=GeoLite2-City-CSV_<date>/GeoLite2-City-Blocks-IPv4.csv -output-file=GeoLite2-City-Blocks-IPv4-with-ranges.csv -include-cidr -include-integer-range```
-- MAGIC 5. Upload the resultant CSV file to Databricks. The queries below assume that you have uploaded the following files to the following tables:
-- MAGIC
-- MAGIC   * `GeoLite2-City-Blocks-IPv4-with-ranges.csv` *uploaded to* `main.geolite2.city_blocks_ipv4_with_ranges`
-- MAGIC   * `GeoLite2-Country-Blocks-IPv4.csv` *uploaded to* `main.geolite2.country_blocks_ipv4_with_ranges`
-- MAGIC   * `GeoLite2-City-Locations-en.csv` *uploaded to* `main.geolite2.city_locations`
-- MAGIC   * `GeoLite2-Country-Locations-en.csv` *uploaded to* `main.geolite2.country_locations`
-- MAGIC 6. Declare the `inet_aton()` function below

-- COMMAND ----------

CREATE OR REPLACE FUNCTION main.geolite2.inet_aton(ip_addr STRING)
  RETURNS BIGINT
  COMMENT "Convert an IP address or CIDR range into a BIGINT"
  RETURN SELECT (
  element_at(regexp_extract_all(ip_addr, "(\\d+)"), 1) * POW(256, 3) +
  element_at(regexp_extract_all(ip_addr, "(\\d+)"), 2) * POW(256, 2) +
  element_at(regexp_extract_all(ip_addr, "(\\d+)"), 3) * POW(256, 1) +
  element_at(regexp_extract_all(ip_addr, "(\\d+)"), 4) * POW(256, 0) 
) 

-- COMMAND ----------

-- https://docs.databricks.com/optimizations/range-join.html
SET spark.databricks.optimizer.rangeJoin.binSize=1024

-- COMMAND ----------

-- All access to Databricks by country
WITH ip_addresses AS (SELECT
  inet_aton(regexp_replace(source_ip_address, '(:\\d*)', '')) AS source_ip_integer,
  COUNT(*) AS total
FROM
  system.access.audit
WHERE
  event_date >= current_date() - INTERVAL 90 DAYS
  AND source_ip_address NOT IN ('', '0.0.0.0')
  AND NOT regexp(source_ip_address, '(^127\.)|(^10\.)|(^172\.1[6-9]\.)|(^172\.2[0-9]\.)|(^172\.3[0-1]\.)|(^192\.168\.)')
GROUP BY 1
)
SELECT /*+ RANGE_JOIN(cb, 1024) */
  cl.country_iso_code AS country,
  SUM(total) AS num_requests
FROM
  ip_addresses ip 
  LEFT JOIN main.geolite2.city_blocks_ipv4_with_ranges cb ON ip.source_ip_integer BETWEEN cb.network_start_integer AND cb.network_last_integer
  LEFT JOIN main.geolite2.city_locations cl ON cb.geoname_id = cl.geoname_id
GROUP BY 1
ORDER BY
  num_requests DESC

-- COMMAND ----------

-- Access to UC securables by country
WITH ip_addresses AS (SELECT
  inet_aton(regexp_replace(source_ip_address, '(:\\d*)', '')) AS source_ip_integer,
  COUNT(*) AS total
FROM
  system.access.audit
WHERE
  event_date >= current_date() - INTERVAL 90 DAYS
  AND action_name IN ('generateTemporaryTableCredential', 'generateTemporaryPathCredential', 'generateTemporaryVolumeCredential', 'deltaSharingQueryTable', 'deltaSharingQueryTableChanges')
  AND source_ip_address NOT IN ('', '0.0.0.0')
  AND NOT regexp(source_ip_address, '(^127\.)|(^10\.)|(^172\.1[6-9]\.)|(^172\.2[0-9]\.)|(^172\.3[0-1]\.)|(^192\.168\.)')
GROUP BY 1
)
SELECT /*+ RANGE_JOIN(cb, 1024) */
  cl.country_iso_code AS country,
  SUM(total) AS num_requests
FROM
  ip_addresses ip 
  LEFT JOIN main.geolite2.city_blocks_ipv4_with_ranges cb ON ip.source_ip_integer BETWEEN cb.network_start_integer AND cb.network_last_integer
  LEFT JOIN main.geolite2.city_locations cl ON cb.geoname_id = cl.geoname_id
GROUP BY 1
ORDER BY
  num_requests DESC

-- COMMAND ----------

-- Access to UC securables by US state
WITH ip_addresses AS (SELECT
  inet_aton(regexp_replace(source_ip_address, '(:\\d*)', '')) AS source_ip_integer,
  COUNT(*) AS total
FROM
  system.access.audit
WHERE
  event_date >= current_date() - INTERVAL 90 DAYS
  AND action_name IN ('generateTemporaryTableCredential', 'generateTemporaryPathCredential', 'generateTemporaryVolumeCredential', 'deltaSharingQueryTable', 'deltaSharingQueryTableChanges')
  AND source_ip_address NOT IN ('', '0.0.0.0')
  AND NOT regexp(source_ip_address, '(^127\.)|(^10\.)|(^172\.1[6-9]\.)|(^172\.2[0-9]\.)|(^172\.3[0-1]\.)|(^192\.168\.)')
GROUP BY 1
)
SELECT /*+ RANGE_JOIN(cb, 1024) */
  cl.subdivision_1_iso_code AS state,
  SUM(total) AS num_requests
FROM
  ip_addresses ip 
  LEFT JOIN main.geolite2.city_blocks_ipv4_with_ranges cb ON ip.source_ip_integer BETWEEN cb.network_start_integer AND cb.network_last_integer
  LEFT JOIN main.geolite2.city_locations cl ON cb.geoname_id = cl.geoname_id
WHERE cl.country_iso_code = 'US'
GROUP BY 1
ORDER BY
  num_requests DESC

-- COMMAND ----------

-- All locations used to access Databricks
WITH ip_addresses AS (SELECT
  inet_aton(regexp_replace(source_ip_address, '(:\\d*)', '')) AS source_ip_integer,
  service_name,
  action_name,
  COUNT(*) AS total
FROM
  system.access.audit
WHERE
  event_date >= current_date() - INTERVAL 90 DAYS
  AND source_ip_address NOT IN ('', '0.0.0.0')
  AND NOT regexp(source_ip_address, '(^127\.)|(^10\.)|(^172\.1[6-9]\.)|(^172\.2[0-9]\.)|(^172\.3[0-1]\.)|(^192\.168\.)')
GROUP BY 1, 2, 3
)
SELECT /*+ RANGE_JOIN(cb, 1024) */
  cl.city_name,
  cb.latitude,
  cb.longitude,
  cb.accuracy_radius,
  service_name,
  action_name,
  SUM(total) AS num_requests
FROM
  ip_addresses ip 
  LEFT JOIN main.geolite2.city_blocks_ipv4_with_ranges cb ON ip.source_ip_integer BETWEEN cb.network_start_integer AND cb.network_last_integer
  LEFT JOIN main.geolite2.city_locations cl ON cb.geoname_id = cl.geoname_id
WHERE cb.latitude IS NOT NULL
AND cb.longitude IS NOT NULL
GROUP BY 1, 2, 3, 4, 5, 6
ORDER BY
  num_requests DESC

-- COMMAND ----------

-- All locations used to access UC securables
WITH ip_addresses AS (SELECT
  inet_aton(regexp_replace(source_ip_address, '(:\\d*)', '')) AS source_ip_integer,
  CASE WHEN isnotnull(request_params.table_full_name) THEN request_params.table_full_name WHEN isnotnull(request_params.volume_full_name) THEN request_params.volume_full_name WHEN isnotnull(request_params.share) THEN request_params.share WHEN isnotnull(request_params.url) THEN request_params.url WHEN isnotnull(request_params.table_url) THEN request_params.table_url WHEN isnotnull(request_params.table_id) THEN request_params.table_id WHEN isnotnull(request_params.volume_id) THEN request_params.volume_id ELSE NULL END AS securable, 
  CASE WHEN isnotnull(request_params.table_full_name) THEN 'TABLE' WHEN isnotnull(request_params.volume_full_name) THEN 'VOLUME' WHEN isnotnull(request_params.share) THEN 'DELTA_SHARE' WHEN isnotnull(request_params.url) THEN 'EXTERNAL_LOCATION' WHEN isnotnull(request_params.table_url) THEN 'TABLE' WHEN isnotnull(request_params.table_id) THEN 'TABLE' WHEN isnotnull(request_params.volume_id) THEN 'VOLUME' ELSE NULL END AS securable_type,
  COUNT(*) AS total
FROM
  system.access.audit
WHERE
  event_date >= current_date() - INTERVAL 90 DAYS
  AND action_name IN ('generateTemporaryTableCredential', 'generateTemporaryPathCredential', 'generateTemporaryVolumeCredential', 'deltaSharingQueryTable', 'deltaSharingQueryTableChanges')
  AND source_ip_address NOT IN ('', '0.0.0.0')
  AND NOT regexp(source_ip_address, '(^127\.)|(^10\.)|(^172\.1[6-9]\.)|(^172\.2[0-9]\.)|(^172\.3[0-1]\.)|(^192\.168\.)')
GROUP BY 1, 2, 3
)
SELECT /*+ RANGE_JOIN(cb, 1024) */
  cl.city_name,
  cb.latitude,
  cb.longitude,
  cb.accuracy_radius,
  securable,
  securable_type,
  SUM(total) AS num_requests
FROM
  ip_addresses ip 
  LEFT JOIN main.geolite2.city_blocks_ipv4_with_ranges cb ON ip.source_ip_integer BETWEEN cb.network_start_integer AND cb.network_last_integer
  LEFT JOIN main.geolite2.city_locations cl ON cb.geoname_id = cl.geoname_id
WHERE cb.latitude IS NOT NULL
AND cb.longitude IS NOT NULL
AND NOT startswith(securable, '__databricks_internal.')
GROUP BY 1, 2, 3, 4, 5, 6
ORDER BY
  num_requests DESC
