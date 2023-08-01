-- Databricks notebook source
-- MAGIC %md
-- MAGIC ## Setup
-- MAGIC 1. Sign up for [GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
-- MAGIC 2. Download the relevant database files
-- MAGIC 3. Download the [GeoIP CSV convertor](https://github.com/maxmind/geoip2-csv-converter)
-- MAGIC 4. Run the geoip2-csv-converter to convert the relevant database files. For example: ```./geoip2-csv-converter -block-file=GeoLite2-City-CSV_<date>/GeoLite2-City-Blocks-IPv4.csv -output-file=GeoLite2-City-Blocks-IPv4-with-ranges.csv -include-cidr -include-integer-range```
-- MAGIC 5. Upload the resultant CSV file to Databricks. The queries below assume that you have uploaded the following files to the following tables:
-- MAGIC
-- MAGIC   * `GeoLite2-City-Blocks-IPv4-with-ranges.csv` **->** `main.geolite2.city_blocks_ipv4_with_ranges`
-- MAGIC   * `GeoLite2-Country-Blocks-IPv4.csv` **->** `main.geolite2.country_blocks_ipv4_with_ranges`
-- MAGIC   * `GeoLite2-City-Locations-en.csv` **->** `main.geolite2.city_locations`
-- MAGIC   * `GeoLite2-Country-Locations-en.csv` **->** `main.geolite2.country_locations`
-- MAGIC 6. Declare the `inet_aton` function below

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
