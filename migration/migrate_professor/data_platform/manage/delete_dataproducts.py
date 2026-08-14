# Databricks notebook source
# MAGIC %run ../common/utils

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Product Deleter
# MAGIC Deletes data products whose status is `created`.
# MAGIC Specify groups to target, or leave empty to delete all created data products.

# COMMAND ----------

# Groups to delete — e.g. ['g101', 'g102']. Leave empty to delete ALL created data products.
groups_to_delete = ['gx00']

# COMMAND ----------

if groups_to_delete:
    groups_filter = "AND group IN (" + ", ".join(f"'{g}'" for g in groups_to_delete) + ")"
else:
    groups_filter = ""

to_delete = spark.sql(f"""
    SELECT group, leader, members, domain_code, domain_name, dp_name
    FROM data_platform.admin.dataproduct_requests
    WHERE status = 'created' {groups_filter}
    ORDER BY group, submitted_at
""").collect()

print(f"Found {len(to_delete)} data product(s) to delete")
for row in to_delete:
    print(f"  - Group {row['group']}: Domain: {row['domain_code']} / Data Product: {row['dp_name']}")

# COMMAND ----------

for row in to_delete:
    group       = row['group']
    leader      = row['leader']
    members     = [m.strip() for m in row['members'].split(',') if m.strip()]
    domain_code = row['domain_code']
    domain_name = row['domain_name']
    dp_name     = row['dp_name']

    try:
        print(f"\n--- {group} / {domain_code} / {dp_name} ---")
        domain = {'code': f'{group.lower()}_{domain_code}', 'name': domain_name}
        generate_dataproduct(domain, dp_name, leader, members, action='delete')
        spark.sql(f"""
            UPDATE data_platform.admin.dataproduct_requests
            SET status = 'deleted', processed_at = current_timestamp()
            WHERE group = '{group}' AND domain_code = '{domain_code}'
                AND dp_name = '{dp_name}' AND status = 'created'
        """)
        print(f"Done.")
    except Exception as e:
        print(f"FAILED: {e}")

# COMMAND ----------

spark.sql("""
    SELECT group, domain_code, domain_name, dp_name, status, submitted_at, processed_at, error
    FROM data_platform.admin.dataproduct_requests
    ORDER BY group, submitted_at
""").display()